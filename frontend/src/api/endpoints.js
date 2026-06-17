import { api } from "./client";

export const auth = {
  login: (email, senha) =>
    api.post("/auth/login", { email, senha }).then((r) => r.data),
  registro: (dados) =>
    api.post("/auth/registro", dados).then((r) => r.data),
  me: () => api.get("/auth/me").then((r) => r.data.usuario),
};

export const produtos = {
  list: (q) => api.get("/produtos/", { params: q ? { q } : undefined }).then((r) => r.data.produtos),
  vencendo: (dias = 7) =>
    api.get("/produtos/vencendo", { params: { dias } }).then((r) => r.data.produtos),
  garantiaVencendo: (dias = 30) =>
    api.get("/produtos/garantia-vencendo", { params: { dias } }).then((r) => r.data.produtos),
  get: (id) => api.get(`/produtos/${id}`).then((r) => r.data.produto),
  create: (body) => api.post("/produtos/", body).then((r) => r.data.produto),
  update: (id, body) => api.put(`/produtos/${id}`, body).then((r) => r.data.produto),
  remove: (id) => api.delete(`/produtos/${id}`).then((r) => r.data),
};

export const comprovantes = {
  list: () => api.get("/comprovantes/").then((r) => r.data.comprovantes),
  get: (id) => api.get(`/comprovantes/${id}`).then((r) => r.data.comprovante),
  upload: (file) => {
    const form = new FormData();
    form.append("arquivo", file);
    return api
      .post("/comprovantes/", form, {
        headers: { "Content-Type": "multipart/form-data" },
        timeout: 60000,
      })
      .then((r) => r.data.comprovante);
  },
  confirmar: (id, produtos) =>
    api.post(`/comprovantes/${id}/confirmar`, { produtos }).then((r) => r.data),
  remove: (id) => api.delete(`/comprovantes/${id}`).then((r) => r.data),
};

export const notificacoes = {
  list: () => api.get("/notificacoes/").then((r) => r.data.notificacoes),
  marcarLida: (id) => api.patch(`/notificacoes/${id}/lida`).then((r) => r.data.notificacao),
  marcarTodasLidas: () => api.patch("/notificacoes/lida-todas").then((r) => r.data),
};

export const categorias = {
  list: () => api.get("/categorias/").then((r) => r.data.categorias),
  create: (body) => api.post("/categorias/", body).then((r) => r.data.categoria),
  update: (id, body) => api.put(`/categorias/${id}`, body).then((r) => r.data.categoria),
  remove: (id) => api.delete(`/categorias/${id}`).then((r) => r.data),
};

export const relatorios = {
  list: () => api.get("/relatorios/").then((r) => r.data.relatorios),
  get: (id) => api.get(`/relatorios/${id}`).then((r) => r.data.relatorio),
  gerar: (tipo) => api.post("/relatorios/", { tipo }).then((r) => r.data.relatorio),
  remove: (id) => api.delete(`/relatorios/${id}`).then((r) => r.data),
};

export const usuarios = {
  list: () => api.get("/usuarios/").then((r) => r.data.usuarios),
  remove: (id) => api.delete(`/usuarios/${id}`).then((r) => r.data),
  notificarVencimentos: (id) =>
    api.post(`/usuarios/${id}/notificar-vencimentos`).then((r) => r.data),
};
