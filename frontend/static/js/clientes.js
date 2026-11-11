
document.addEventListener("DOMContentLoaded", () => {

    // ==========================================
    // ELEMENTOS DEL MODAL DE CLIENTES
    // ==========================================

    const modalCliente = document.getElementById("modalCliente");
    const formCliente = document.getElementById("formCliente");
    const tituloModal = document.getElementById("tituloModalCliente");
    const textoGuardar = document.getElementById("textoGuardar");

    const urlCrear = formCliente.action;


    // ==========================================
    // NUEVO CLIENTE
    // ==========================================

    document.getElementById("btnNuevoCliente")
        .addEventListener("click", () => {

            formCliente.reset();
            formCliente.action = urlCrear;

            tituloModal.textContent = "Nuevo cliente";
            textoGuardar.textContent = "Guardar cliente";

        });


    // ==========================================
    // EDITAR CLIENTE
    // ==========================================

    document.querySelectorAll(".btn-editar").forEach(boton => {

        boton.addEventListener("click", () => {

            formCliente.reset();

            formCliente.action = boton.dataset.url;

            document.getElementById("clienteNombre").value =
                boton.dataset.nombre;

            document.getElementById("clientePais").value =
                boton.dataset.pais;

            document.getElementById("clienteEmail").value =
                boton.dataset.email;

            document.getElementById("clienteTelefono").value =
                boton.dataset.telefono;

            document.getElementById("clienteCiudad").value =
                boton.dataset.ciudad;

            document.getElementById("clienteDireccion").value =
                boton.dataset.direccion;

            tituloModal.textContent = "Editar cliente";
            textoGuardar.textContent = "Guardar cambios";

            bootstrap.Modal.getOrCreateInstance(modalCliente).show();

        });

    });


    // ==========================================
    // ELIMINAR CLIENTE
    // ==========================================

    const modalEliminar = document.getElementById("modalEliminar");
    const formEliminar = document.getElementById("formEliminar");

    document.querySelectorAll(".btn-eliminar").forEach(boton => {

        boton.addEventListener("click", () => {

            document.getElementById("nombreEliminar").textContent =
                boton.dataset.nombre;

            formEliminar.action = boton.dataset.url;

            bootstrap.Modal.getOrCreateInstance(modalEliminar).show();

        });

    });


    // ==========================================
    // IMPRIMIR REPORTE DE NACIONALIDAD
    // SIN ABRIR OTRA PESTAÑA
    // ==========================================

    const btnImprimirReporte = document.getElementById(
        "btnImprimirReporte"
    );

    const documentoReporte = document.getElementById(
        "documentoReporte"
    );

    if (btnImprimirReporte && documentoReporte) {

        btnImprimirReporte.addEventListener("click", () => {

            // Eliminar estilos de impresión anteriores
            document.getElementById(
                "estilosImpresionReporte"
            )?.remove();

            // Crear estilos exclusivos para impresión
            const estilosImpresion = document.createElement("style");

            estilosImpresion.id = "estilosImpresionReporte";

            estilosImpresion.textContent = `
                @media print {

                    @page {
                        size: A4;
                        margin: 15mm;
                    }

                    html,
                    body {
                        height: auto !important;
                        overflow: visible !important;
                    }

                    body * {
                        visibility: hidden !important;
                    }

                    #modalReporte,
                    #documentoReporte,
                    #documentoReporte * {
                        visibility: visible !important;
                    }

                    #modalReporte {
                        display: block !important;
                        position: absolute !important;
                        top: 0 !important;
                        left: 0 !important;
                        width: 100% !important;
                        height: auto !important;
                        margin: 0 !important;
                        padding: 0 !important;
                        overflow: visible !important;
                    }

                    #modalReporte .modal-dialog {
                        position: static !important;
                        transform: none !important;
                        width: 100% !important;
                        max-width: 100% !important;
                        margin: 0 !important;
                    }

                    #modalReporte .modal-content {
                        position: static !important;
                        width: 100% !important;
                        height: auto !important;
                        border: none !important;
                        box-shadow: none !important;
                        background: white !important;
                        overflow: visible !important;
                    }

                    #modalReporte .modal-body {
                        padding: 0 !important;
                        margin: 0 !important;
                        height: auto !important;
                        max-height: none !important;
                        overflow: visible !important;
                    }

                    #documentoReporte {
                        position: static !important;
                        width: 100% !important;
                        max-width: 100% !important;
                        margin: 0 !important;
                        padding: 0 !important;
                        border: none !important;
                        box-shadow: none !important;
                        overflow: visible !important;
                    }

                    #modalReporte .modal-header,
                    #modalReporte .modal-footer,
                    .modal-backdrop {
                        display: none !important;
                    }

                    #documentoReporte .table-responsive {
                        overflow: visible !important;
                    }

                    #documentoReporte table {
                        width: 100% !important;
                        border-collapse: collapse !important;
                    }

                    #documentoReporte tr {
                        break-inside: avoid;
                    }

                    #documentoReporte {
                        print-color-adjust: exact;
                        -webkit-print-color-adjust: exact;
                    }

                }
            `;

            document.head.appendChild(estilosImpresion);


            // ==========================================
            // NOMBRE PERSONALIZADO DEL REPORTE
            // ==========================================

            const tituloOriginal = document.title;

            // Nombre sugerido al guardar como PDF
            document.title = "Reporte_Nacionalidad_CandyKane";

            // Restaurar el título después de imprimir
            const restaurarTitulo = () => {

                document.title = tituloOriginal;

                window.removeEventListener(
                    "afterprint",
                    restaurarTitulo
                );

            };

            window.addEventListener(
                "afterprint",
                restaurarTitulo,
                { once: true }
            );

            // Abrir cuadro normal de impresión
            window.print();

        });

    }

});
