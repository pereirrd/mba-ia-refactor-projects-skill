function notFoundHandler(req, res) {
  res.status(404).json({ error: "Não encontrado" });
}

function errorHandler(err, req, res, next) {
  console.error("[ERROR]", err);
  if (res.headersSent) {
    return next(err);
  }
  res.status(500).json({ error: "Erro interno" });
}

module.exports = { notFoundHandler, errorHandler };
