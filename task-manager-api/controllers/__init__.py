from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import joinedload

from config.settings import settings
from database import db
from models.category import Category
from models.task import Task, utcnow
from models.user import User
from services.notification_service import notification_service
from utils.helpers import parse_date, process_task_data, validate_email


class TaskController:
    def list_tasks(self):
        tasks = Task.query.options(
            joinedload(Task.user), joinedload(Task.category)
        ).all()
        return [task.to_dict(include_relations=True) for task in tasks], 200

    def get_task(self, task_id):
        task = db.session.get(Task, task_id)
        if not task:
            return {"error": "Task não encontrada"}, 404
        return task.to_dict(include_relations=True), 200

    def create_task(self, data):
        if not data:
            return {"error": "Dados inválidos"}, 400

        title = data.get("title")
        if not title:
            return {"error": "Título é obrigatório"}, 400
        if len(title) < settings.MIN_TITLE_LENGTH:
            return {"error": "Título muito curto"}, 400
        if len(title) > settings.MAX_TITLE_LENGTH:
            return {"error": "Título muito longo"}, 400

        status = data.get("status", "pending")
        priority = data.get("priority", settings.DEFAULT_PRIORITY)
        user_id = data.get("user_id")
        category_id = data.get("category_id")

        if status not in settings.VALID_STATUSES:
            return {"error": "Status inválido"}, 400
        if priority < 1 or priority > 5:
            return {"error": "Prioridade deve ser entre 1 e 5"}, 400

        if user_id and not db.session.get(User, user_id):
            return {"error": "Usuário não encontrado"}, 404
        if category_id and not db.session.get(Category, category_id):
            return {"error": "Categoria não encontrada"}, 404

        task = Task(
            title=title,
            description=data.get("description", ""),
            status=status,
            priority=priority,
            user_id=user_id,
            category_id=category_id,
        )

        if data.get("due_date"):
            parsed = parse_date(data["due_date"])
            if not parsed:
                return {"error": "Formato de data inválido. Use YYYY-MM-DD"}, 400
            task.due_date = parsed

        tags = data.get("tags")
        if tags:
            task.tags = ",".join(tags) if isinstance(tags, list) else tags

        db.session.add(task)
        db.session.commit()

        if task.user_id:
            notification_service.notify_task_assigned(
                db.session.get(User, task.user_id), task
            )

        return task.to_dict(), 201

    def update_task(self, task_id, data):
        task = db.session.get(Task, task_id)
        if not task:
            return {"error": "Task não encontrada"}, 404
        if not data:
            return {"error": "Dados inválidos"}, 400

        payload, error = process_task_data(data)
        if error:
            return {"error": error}, 400

        if "title" in payload:
            task.title = payload["title"]
        if "description" in payload:
            task.description = payload["description"]
        if "status" in payload:
            task.status = payload["status"]
        if "priority" in payload:
            task.priority = payload["priority"]
        if "due_date" in payload:
            task.due_date = payload["due_date"]
        if "tags" in payload:
            task.tags = payload["tags"]

        if "user_id" in data:
            if data["user_id"] and not db.session.get(User, data["user_id"]):
                return {"error": "Usuário não encontrado"}, 404
            task.user_id = data["user_id"]

        if "category_id" in data:
            if data["category_id"] and not db.session.get(Category, data["category_id"]):
                return {"error": "Categoria não encontrada"}, 404
            task.category_id = data["category_id"]

        task.updated_at = utcnow()
        db.session.commit()
        return task.to_dict(), 200

    def delete_task(self, task_id):
        task = db.session.get(Task, task_id)
        if not task:
            return {"error": "Task não encontrada"}, 404
        db.session.delete(task)
        db.session.commit()
        return {"message": "Task deletada com sucesso"}, 200

    def search_tasks(self, args):
        query = args.get("q", "")
        status = args.get("status", "")
        priority = args.get("priority", "")
        user_id = args.get("user_id", "")

        tasks = Task.query
        if query:
            tasks = tasks.filter(
                db.or_(
                    Task.title.like(f"%{query}%"),
                    Task.description.like(f"%{query}%"),
                )
            )
        if status:
            tasks = tasks.filter(Task.status == status)
        if priority:
            tasks = tasks.filter(Task.priority == int(priority))
        if user_id:
            tasks = tasks.filter(Task.user_id == int(user_id))

        return [task.to_dict() for task in tasks.all()], 200

    def stats(self):
        total = Task.query.count()
        pending = Task.query.filter_by(status="pending").count()
        in_progress = Task.query.filter_by(status="in_progress").count()
        done = Task.query.filter_by(status="done").count()
        cancelled = Task.query.filter_by(status="cancelled").count()
        overdue_count = sum(1 for task in Task.query.all() if task.is_overdue())

        return {
            "total": total,
            "pending": pending,
            "in_progress": in_progress,
            "done": done,
            "cancelled": cancelled,
            "overdue": overdue_count,
            "completion_rate": round((done / total) * 100, 2) if total > 0 else 0,
        }, 200


class UserController:
    def list_users(self):
        users = User.query.all()
        result = []
        for user in users:
            data = user.to_dict()
            data["task_count"] = len(user.tasks)
            result.append(data)
        return result, 200

    def get_user(self, user_id):
        user = db.session.get(User, user_id)
        if not user:
            return {"error": "Usuário não encontrado"}, 404
        data = user.to_dict()
        data["tasks"] = [task.to_dict() for task in Task.query.filter_by(user_id=user_id).all()]
        return data, 200

    def create_user(self, data):
        if not data:
            return {"error": "Dados inválidos"}, 400

        name = data.get("name")
        email = data.get("email")
        password = data.get("password")
        role = data.get("role", "user")

        if not name:
            return {"error": "Nome é obrigatório"}, 400
        if not email:
            return {"error": "Email é obrigatório"}, 400
        if not password:
            return {"error": "Senha é obrigatória"}, 400
        if not validate_email(email):
            return {"error": "Email inválido"}, 400
        if len(password) < settings.MIN_PASSWORD_LENGTH:
            return {"error": "Senha deve ter no mínimo 4 caracteres"}, 400
        if User.query.filter_by(email=email).first():
            return {"error": "Email já cadastrado"}, 409
        if role not in settings.VALID_ROLES:
            return {"error": "Role inválido"}, 400

        user = User(name=name, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user.to_dict(), 201

    def update_user(self, user_id, data):
        user = db.session.get(User, user_id)
        if not user:
            return {"error": "Usuário não encontrado"}, 404
        if not data:
            return {"error": "Dados inválidos"}, 400

        if "name" in data:
            user.name = data["name"]
        if "email" in data:
            if not validate_email(data["email"]):
                return {"error": "Email inválido"}, 400
            existing = User.query.filter_by(email=data["email"]).first()
            if existing and existing.id != user_id:
                return {"error": "Email já cadastrado"}, 409
            user.email = data["email"]
        if "password" in data:
            if len(data["password"]) < settings.MIN_PASSWORD_LENGTH:
                return {"error": "Senha muito curta"}, 400
            user.set_password(data["password"])
        if "role" in data:
            if data["role"] not in settings.VALID_ROLES:
                return {"error": "Role inválido"}, 400
            user.role = data["role"]
        if "active" in data:
            user.active = data["active"]

        db.session.commit()
        return user.to_dict(), 200

    def delete_user(self, user_id):
        user = db.session.get(User, user_id)
        if not user:
            return {"error": "Usuário não encontrado"}, 404

        for task in Task.query.filter_by(user_id=user_id).all():
            db.session.delete(task)
        db.session.delete(user)
        db.session.commit()
        return {"message": "Usuário deletado com sucesso"}, 200

    def get_user_tasks(self, user_id):
        user = db.session.get(User, user_id)
        if not user:
            return {"error": "Usuário não encontrado"}, 404
        tasks = Task.query.filter_by(user_id=user_id).all()
        return [task.to_dict() for task in tasks], 200

    def login(self, data):
        if not data:
            return {"error": "Dados inválidos"}, 400
        email = data.get("email")
        password = data.get("password")
        if not email or not password:
            return {"error": "Email e senha são obrigatórios"}, 400

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            return {"error": "Credenciais inválidas"}, 401
        if not user.active:
            return {"error": "Usuário inativo"}, 403

        token = f"session-token-{user.id}"
        return {
            "message": "Login realizado com sucesso",
            "user": user.to_dict(),
            "token": token,
        }, 200


class ReportController:
    def summary(self):
        total_tasks = Task.query.count()
        total_users = User.query.count()
        total_categories = Category.query.count()

        pending = Task.query.filter_by(status="pending").count()
        in_progress = Task.query.filter_by(status="in_progress").count()
        done = Task.query.filter_by(status="done").count()
        cancelled = Task.query.filter_by(status="cancelled").count()

        priorities = {
            "critical": Task.query.filter_by(priority=1).count(),
            "high": Task.query.filter_by(priority=2).count(),
            "medium": Task.query.filter_by(priority=3).count(),
            "low": Task.query.filter_by(priority=4).count(),
            "minimal": Task.query.filter_by(priority=5).count(),
        }

        overdue_list = []
        for task in Task.query.all():
            if task.is_overdue():
                due = task.due_date
                if due.tzinfo is None:
                    due = due.replace(tzinfo=timezone.utc)
                overdue_list.append(
                    {
                        "id": task.id,
                        "title": task.title,
                        "due_date": str(task.due_date),
                        "days_overdue": (utcnow() - due).days,
                    }
                )

        seven_days_ago = utcnow() - timedelta(days=7)
        recent_tasks = Task.query.filter(Task.created_at >= seven_days_ago).count()
        recent_done = Task.query.filter(
            Task.status == "done", Task.updated_at >= seven_days_ago
        ).count()

        user_stats = []
        for user in User.query.all():
            user_tasks = Task.query.filter_by(user_id=user.id).all()
            total = len(user_tasks)
            completed = sum(1 for task in user_tasks if task.status == "done")
            user_stats.append(
                {
                    "user_id": user.id,
                    "user_name": user.name,
                    "total_tasks": total,
                    "completed_tasks": completed,
                    "completion_rate": round((completed / total) * 100, 2) if total else 0,
                }
            )

        return {
            "generated_at": str(utcnow()),
            "overview": {
                "total_tasks": total_tasks,
                "total_users": total_users,
                "total_categories": total_categories,
            },
            "tasks_by_status": {
                "pending": pending,
                "in_progress": in_progress,
                "done": done,
                "cancelled": cancelled,
            },
            "tasks_by_priority": priorities,
            "overdue": {"count": len(overdue_list), "tasks": overdue_list},
            "recent_activity": {
                "tasks_created_last_7_days": recent_tasks,
                "tasks_completed_last_7_days": recent_done,
            },
            "user_productivity": user_stats,
        }, 200

    def user_report(self, user_id):
        user = db.session.get(User, user_id)
        if not user:
            return {"error": "Usuário não encontrado"}, 404

        tasks = Task.query.filter_by(user_id=user_id).all()
        done = sum(1 for task in tasks if task.status == "done")
        pending = sum(1 for task in tasks if task.status == "pending")
        in_progress = sum(1 for task in tasks if task.status == "in_progress")
        cancelled = sum(1 for task in tasks if task.status == "cancelled")
        overdue = sum(1 for task in tasks if task.is_overdue())
        high_priority = sum(1 for task in tasks if task.priority <= 2)
        total = len(tasks)

        return {
            "user": {"id": user.id, "name": user.name, "email": user.email},
            "statistics": {
                "total_tasks": total,
                "done": done,
                "pending": pending,
                "in_progress": in_progress,
                "cancelled": cancelled,
                "overdue": overdue,
                "high_priority": high_priority,
                "completion_rate": round((done / total) * 100, 2) if total else 0,
            },
        }, 200


class CategoryController:
    def list_categories(self):
        result = []
        for category in Category.query.all():
            data = category.to_dict()
            data["task_count"] = Task.query.filter_by(category_id=category.id).count()
            result.append(data)
        return result, 200

    def create_category(self, data):
        if not data:
            return {"error": "Dados inválidos"}, 400
        name = data.get("name")
        if not name:
            return {"error": "Nome é obrigatório"}, 400

        category = Category(
            name=name,
            description=data.get("description", ""),
            color=data.get("color", settings.DEFAULT_COLOR),
        )
        db.session.add(category)
        db.session.commit()
        return category.to_dict(), 201

    def update_category(self, cat_id, data):
        category = db.session.get(Category, cat_id)
        if not category:
            return {"error": "Categoria não encontrada"}, 404
        if not data:
            return {"error": "Dados inválidos"}, 400

        if "name" in data:
            category.name = data["name"]
        if "description" in data:
            category.description = data["description"]
        if "color" in data:
            category.color = data["color"]

        db.session.commit()
        return category.to_dict(), 200

    def delete_category(self, cat_id):
        category = db.session.get(Category, cat_id)
        if not category:
            return {"error": "Categoria não encontrada"}, 404

        Task.query.filter_by(category_id=cat_id).update({"category_id": None})
        db.session.delete(category)
        db.session.commit()
        return {"message": "Categoria deletada"}, 200


task_controller = TaskController()
user_controller = UserController()
report_controller = ReportController()
category_controller = CategoryController()
