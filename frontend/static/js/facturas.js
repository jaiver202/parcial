
document.addEventListener("DOMContentLoaded", () => {

    // ==========================================
    // ELEMENTOS DEL MODAL
    // ==========================================

    const modalElemento = document.getElementById(
        "modalDetalleFactura"
    );

    const modalFactura = new bootstrap.Modal(
        modalElemento
    );

    const contenido = document.getElementById(
        "contenidoModalFactura"
    );

    const titulo = document.getElementById(
        "tituloModalFactura"
    );

    const btnImprimir = document.getElementById(
        "btnImprimirFactura"
    );

    const config = document.getElementById(
        "configFacturas"
    );

    // URL para consultar el detalle de la factura
    const URL_BASE = config.dataset.urlBase;

    let idFacturaActual = null;
    let controladorActual = null;

    // NUEVO: nombre de la factura seleccionada
    let nombreFacturaActual = null;


    // ==========================================
    // CONSTRUIR URL SEGÚN ID DE VENTA
    // ==========================================

    function construirUrl(urlBase, idVenta) {

        return urlBase.replace(
            /\/0(?=\/|$|\?)/,
            "/" + encodeURIComponent(idVenta)
        );

    }


    // ==========================================
    // ABRIR FACTURA EN MODAL
    // ==========================================

    document.querySelectorAll(".abrir-factura").forEach(
        elemento => {

            elemento.addEventListener("click", async (event) => {

                event.preventDefault();

                const idVenta = elemento.dataset.id;

                if (!idVenta) return;

                // Cancelar una solicitud anterior
                if (controladorActual) {
                    controladorActual.abort();
                }

                controladorActual = new AbortController();

                const controlador = controladorActual;

                idFacturaActual = null;
                nombreFacturaActual = null;

                btnImprimir.disabled = true;

                titulo.textContent = "Detalle de factura";

                contenido.innerHTML = `
                    <div class="text-center py-5">
                        <div class="spinner-border text-secondary"
                             role="status"></div>

                        <p class="mt-3 text-muted">
                            Cargando factura...
                        </p>
                    </div>
                `;

                modalFactura.show();

                try {

                    // Construir URL del detalle HTML
                    const urlDetalle = construirUrl(
                        URL_BASE,
                        idVenta
                    );

                    // Consultar la factura
                    const respuesta = await fetch(urlDetalle, {
                        headers: {
                            "X-Requested-With": "XMLHttpRequest"
                        },
                        signal: controlador.signal
                    });

                    if (!respuesta.ok) {
                        throw new Error(
                            "No se pudo cargar la factura."
                        );
                    }

                    const html = await respuesta.text();

                    const documento = new DOMParser()
                        .parseFromString(html, "text/html");

                    // Extraer únicamente el comprobante
                    const comprobante = documento.querySelector(
                        ".factura-documento"
                    );

                    if (!comprobante) {
                        throw new Error(
                            "No se encontró el comprobante de la factura."
                        );
                    }

                    // Mostrar factura dentro del modal
                    contenido.replaceChildren(
                        comprobante.cloneNode(true)
                    );

                    // Obtener número de factura
                    const numero = elemento.closest("tr")
                        ?.querySelector(".enlace-factura")
                        ?.textContent.trim();

                    // NUEVO: guardar el nombre correspondiente
                    nombreFacturaActual = numero
                        ? numero
                        : `Factura-${idVenta}`;

                    titulo.textContent = numero
                        ? "Factura " + numero
                        : "Detalle de factura";

                    // Guardar ID de factura
                    idFacturaActual = idVenta;

                    // Habilitar botón Imprimir
                    btnImprimir.disabled = false;

                } catch (error) {

                    if (error.name === "AbortError") {
                        return;
                    }

                    contenido.innerHTML = `
                        <div class="alert alert-danger">
                            No se pudo cargar el comprobante.
                        </div>
                    `;

                    console.error(error);

                    btnImprimir.disabled = true;
                }

            });

        }
    );


    // ==========================================
    // IMPRIMIR FACTURA SIN ABRIR OTRA PESTAÑA
    // ==========================================

    btnImprimir.addEventListener("click", () => {

        if (!idFacturaActual) {
            alert("Primero selecciona una factura.");
            return;
        }

        const comprobante = contenido.querySelector(
            ".factura-documento"
        );

        if (!comprobante) {
            alert("No se encontró el comprobante.");
            return;
        }

        // Eliminar estilos de impresión anteriores
        document.getElementById(
            "estilosImpresionFactura"
        )?.remove();

        // Crear estilos para imprimir solo la factura
        const estilosImpresion = document.createElement("style");

        estilosImpresion.id = "estilosImpresionFactura";

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

                #modalDetalleFactura,
                #modalDetalleFactura #contenidoModalFactura,
                #modalDetalleFactura #contenidoModalFactura * {
                    visibility: visible !important;
                }

                #modalDetalleFactura {
                    display: block !important;
                    position: absolute !important;
                    inset: 0 auto auto 0 !important;
                    width: 100% !important;
                    height: auto !important;
                    overflow: visible !important;
                    padding: 0 !important;
                    margin: 0 !important;
                }

                #modalDetalleFactura .modal-dialog {
                    position: static !important;
                    transform: none !important;
                    max-width: 100% !important;
                    width: 100% !important;
                    margin: 0 !important;
                }

                #modalDetalleFactura .modal-content {
                    position: static !important;
                    border: none !important;
                    box-shadow: none !important;
                    background: white !important;
                    overflow: visible !important;
                    height: auto !important;
                }

                #modalDetalleFactura .modal-body {
                    padding: 0 !important;
                    margin: 0 !important;
                    overflow: visible !important;
                    max-height: none !important;
                }

                #contenidoModalFactura {
                    position: static !important;
                    width: 100% !important;
                    height: auto !important;
                    overflow: visible !important;
                    padding: 0 !important;
                    margin: 0 !important;
                }

                #contenidoModalFactura .factura-documento {
                    width: 100% !important;
                    max-width: 100% !important;
                    margin: 0 !important;
                    box-shadow: none !important;
                    border: none !important;
                }

                #modalDetalleFactura .modal-header,
                #modalDetalleFactura .modal-footer,
                .modal-backdrop {
                    display: none !important;
                }

                #contenidoModalFactura table {
                    width: 100% !important;
                    border-collapse: collapse !important;
                }

                #contenidoModalFactura tr {
                    break-inside: avoid;
                }

                #contenidoModalFactura {
                    print-color-adjust: exact;
                    -webkit-print-color-adjust: exact;
                }
            }
        `;

        document.head.appendChild(estilosImpresion);


        // ==========================================
        // NUEVO: NOMBRE PERSONALIZADO DEL PDF
        // ==========================================

        // Guardar el título original de la página
        const tituloOriginal = document.title;

        // Utilizar el número de factura como nombre
        document.title = nombreFacturaActual ||
            `Factura-${idFacturaActual}`;

        // Restaurar el título al terminar la impresión
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

        // Abrir el cuadro normal de impresión
        window.print();

    });


    // ==========================================
    // LIMPIAR MODAL AL CERRAR
    // ==========================================

    modalElemento.addEventListener(
        "hidden.bs.modal",
        () => {

            if (controladorActual) {
                controladorActual.abort();
                controladorActual = null;
            }

            idFacturaActual = null;

            // NUEVO: limpiar el nombre de factura
            nombreFacturaActual = null;

            btnImprimir.disabled = true;

            titulo.textContent = "Detalle de factura";

            contenido.replaceChildren();

        }
    );

});
