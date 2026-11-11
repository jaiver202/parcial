
document.addEventListener("DOMContentLoaded", () => {

    const modalEditar = new bootstrap.Modal(
        document.getElementById("modalEditarUsuario")
    );

    const formEditar = document.getElementById("formEditarUsuario");

    const nombre = document.getElementById("editarNombre");
    const email = document.getElementById("editarEmail");
    const rol = document.getElementById("editarRol");
    const estado = document.getElementById("editarEstado");
    const estadoValor = document.getElementById("editarEstadoValor");

    // ABRIR MODAL PARA EDITAR
    document.querySelectorAll(".btn-editar").forEach(boton => {

        boton.addEventListener("click", () => {

            formEditar.action = boton.dataset.url;

            nombre.value = boton.dataset.nombre;
            email.value = boton.dataset.email;
            rol.value = boton.dataset.rol;

            estado.checked = boton.dataset.estado === "activo";
            estadoValor.value = estado.checked ? "activo" : "inactivo";

            formEditar.querySelector(
                'input[name="contrasena"]'
            ).value = "";

            modalEditar.show();
        });
    });

    // CAMBIAR ESTADO
    estado.addEventListener("change", () => {
        estadoValor.value = estado.checked ? "activo" : "inactivo";
    });

    // CONFIRMAR ELIMINACIÓN
    document.querySelectorAll(".form-eliminar").forEach(form => {

        form.addEventListener("submit", event => {

            const confirmar = window.confirm(
                "¿Seguro que deseas eliminar este usuario?"
            );

            if (!confirmar) {
                event.preventDefault();
            }
        });
    });
});
