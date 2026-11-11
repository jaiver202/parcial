
document.addEventListener("DOMContentLoaded", () => {

    // ==========================================
    // 1. CONFIGURACIÓN DE FLASK
    // ==========================================

    const configVentas = document.getElementById("configVentas");

    const URL_COBRAR = configVentas.dataset.urlCobrar;

    const csrfToken = document.querySelector(
        'meta[name="csrf-token"]'
    ).content;


    // ==========================================
    // 2. VARIABLES DEL CARRITO
    // ==========================================

    const carrito = new Map();

    const listaPedido = document.getElementById("listaPedido");
    const totalPedido = document.getElementById("totalPedido");
    const btnCobrar = document.getElementById("btnCobrar");
    const clienteVenta = document.getElementById("clienteVenta");
    const metodoPago = document.getElementById("metodoPago");
    const mensajeVenta = document.getElementById("mensajeVenta");


    // ==========================================
    // 3. MODAL DE CONFIRMACIÓN
    // ==========================================

    const modalConfirmarElemento = document.getElementById(
        "modalConfirmarVenta"
    );

    const modalConfirmar = new bootstrap.Modal(
        modalConfirmarElemento
    );

    const btnConfirmarVenta = document.getElementById(
        "btnConfirmarVenta"
    );

    const confirmarCliente = document.getElementById(
        "confirmarCliente"
    );

    const confirmarProductos = document.getElementById(
        "confirmarProductos"
    );

    const confirmarMetodo = document.getElementById(
        "confirmarMetodo"
    );

    const confirmarTotal = document.getElementById(
        "confirmarTotal"
    );

    // Evitar registrar dos veces la misma venta
    let procesandoVenta = false;


    // ==========================================
    // 4. FORMATO DE PRECIOS
    // ==========================================

    const formatoPrecio = new Intl.NumberFormat("es-CO", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });

    const dinero = valor => "$ " + formatoPrecio.format(valor);


    // ==========================================
    // 5. MOSTRAR MENSAJES
    // ==========================================

    function mostrarMensaje(mensaje, tipo = "info") {

        mensajeVenta.replaceChildren();

        const alerta = document.createElement("div");

        alerta.className = `alert alert-${tipo}`;
        alerta.textContent = mensaje;

        mensajeVenta.appendChild(alerta);
    }


    // ==========================================
    // 6. CAMBIAR CANTIDAD DE PRODUCTOS
    // ==========================================

    function cambiarCantidad(id, cambio) {

        if (procesandoVenta) return;

        const producto = carrito.get(id);

        if (!producto) return;

        const nuevaCantidad = producto.cantidad + cambio;

        // Validar existencias
        if (nuevaCantidad > producto.stock) {

            mostrarMensaje(
                "No hay más existencias disponibles de " +
                producto.nombre,
                "warning"
            );

            return;
        }

        // Eliminar producto si llega a cero
        if (nuevaCantidad <= 0) {

            carrito.delete(id);

        } else {

            producto.cantidad = nuevaCantidad;
        }

        renderizarPedido();
    }


    // ==========================================
    // 7. MOSTRAR PRODUCTOS EN EL CARRITO
    // ==========================================

    function renderizarPedido() {

        listaPedido.replaceChildren();

        let total = 0;

        // Mostrar carrito vacío
        if (carrito.size === 0) {

            const contenedorVacio = document.createElement("div");
            contenedorVacio.className = "pedido-vacio";

            const icono = document.createElement("i");
            icono.className = "bi bi-cart3";

            const mensaje = document.createElement("p");
            mensaje.textContent = "Tu pedido está vacío";

            contenedorVacio.append(icono, mensaje);

            listaPedido.appendChild(contenedorVacio);
        }

        // Recorrer productos agregados
        carrito.forEach(producto => {

            const subtotal = producto.precio * producto.cantidad;

            total += subtotal;

            const fila = document.createElement("div");
            fila.className = "pedido-item";

            // Información del producto
            const informacion = document.createElement("div");

            const nombre = document.createElement("strong");
            nombre.textContent = producto.nombre;

            const precio = document.createElement("small");
            precio.textContent = dinero(subtotal);

            informacion.append(nombre, precio);

            // Controles de cantidad
            const controles = document.createElement("div");
            controles.className = "cantidad-controles";

            // Botón disminuir
            const menos = document.createElement("button");

            menos.type = "button";
            menos.textContent = "−";
            menos.disabled = procesandoVenta;

            menos.setAttribute(
                "aria-label",
                "Quitar una unidad de " + producto.nombre
            );

            menos.addEventListener("click", () => {
                cambiarCantidad(producto.id, -1);
            });

            // Cantidad actual
            const cantidad = document.createElement("span");

            cantidad.textContent = producto.cantidad;

            // Botón aumentar
            const mas = document.createElement("button");

            mas.type = "button";
            mas.textContent = "+";

            mas.setAttribute(
                "aria-label",
                "Agregar una unidad de " + producto.nombre
            );

            mas.disabled = (
                procesandoVenta ||
                producto.cantidad >= producto.stock
            );

            mas.addEventListener("click", () => {
                cambiarCantidad(producto.id, 1);
            });

            controles.append(menos, cantidad, mas);

            fila.append(informacion, controles);

            listaPedido.appendChild(fila);
        });

        // Actualizar total
        totalPedido.textContent = dinero(total);

        // Habilitar cobro si hay cliente y productos
        btnCobrar.disabled = (
            procesandoVenta ||
            carrito.size === 0 ||
            !clienteVenta.value
        );
    }


    // ==========================================
    // 8. AGREGAR PRODUCTOS AL CARRITO
    // ==========================================

    document.querySelectorAll(".producto-card").forEach(card => {

        const boton = card.querySelector(".btn-agregar");

        if (!boton) return;

        boton.addEventListener("click", () => {

            if (procesandoVenta) return;

            const id = Number(card.dataset.id);
            const stock = Number(card.dataset.stock);

            // Producto ya agregado
            if (carrito.has(id)) {

                cambiarCantidad(id, 1);
                return;
            }

            // Validar inventario
            if (stock <= 0) {

                mostrarMensaje(
                    "Este producto no tiene existencias disponibles.",
                    "warning"
                );

                return;
            }

            // Agregar producto
            carrito.set(id, {
                id: id,
                nombre: card.dataset.nombre,
                precio: Number(card.dataset.precio),
                stock: stock,
                cantidad: 1
            });

            renderizarPedido();
        });
    });


    // ==========================================
    // 9. CAMBIO DE CLIENTE
    // ==========================================

    clienteVenta.addEventListener("change", () => {
        renderizarPedido();
    });


    // ==========================================
    // 10. ABRIR MODAL DE CONFIRMACIÓN
    // ==========================================

    btnCobrar.addEventListener("click", () => {

        // Validar pedido
        if (carrito.size === 0 || !clienteVenta.value) {

            mostrarMensaje(
                "Debes seleccionar un cliente y agregar productos.",
                "warning"
            );

            return;
        }

        if (procesandoVenta) return;

        // Obtener nombre del cliente
        const nombreCliente =
            clienteVenta.options[
                clienteVenta.selectedIndex
            ].text.trim();

        // Calcular cantidad de productos
        const cantidadProductos = Array.from(
            carrito.values()
        ).reduce(
            (total, producto) => total + producto.cantidad,
            0
        );

        // Calcular total
        const total = Array.from(
            carrito.values()
        ).reduce(
            (suma, producto) =>
                suma + producto.precio * producto.cantidad,
            0
        );

        // Mostrar datos en el modal
        confirmarCliente.textContent = nombreCliente;

        confirmarProductos.textContent =
            cantidadProductos + " unidades";

        confirmarMetodo.textContent = metodoPago.value;

        confirmarTotal.textContent = dinero(total);

        // Abrir modal personalizado
        modalConfirmar.show();
    });


    // ==========================================
    // 11. CONFIRMAR Y REGISTRAR VENTA
    // ==========================================

    btnConfirmarVenta.addEventListener("click", async () => {

        // Evitar doble registro
        if (procesandoVenta) return;

        // Validar pedido
        if (carrito.size === 0 || !clienteVenta.value) {

            modalConfirmar.hide();

            mostrarMensaje(
                "El pedido no es válido.",
                "warning"
            );

            return;
        }

        // Bloquear mientras se registra
        procesandoVenta = true;

        btnConfirmarVenta.disabled = true;
        btnCobrar.disabled = true;

        const textoOriginal = btnConfirmarVenta.innerHTML;

        btnConfirmarVenta.textContent = "Procesando venta...";

        // Preparar productos
        const items = Array.from(
            carrito.values()
        ).map(producto => ({
            id_producto: producto.id,
            cantidad: producto.cantidad
        }));

        try {

            // Enviar venta al backend Flask
            const respuesta = await fetch(URL_COBRAR, {

                method: "POST",

                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken
                },

                body: JSON.stringify({
                    id_cliente: Number(clienteVenta.value),
                    metodo_pago: metodoPago.value,
                    items: items
                })
            });

            // Leer respuesta
            const datos = await respuesta.json();

            // Validar respuesta
            if (!respuesta.ok || !datos.ok) {

                throw new Error(
                    datos.mensaje ||
                    "No se pudo registrar la venta."
                );
            }

            // Verificar dirección de factura
            if (!datos.url_factura) {

                throw new Error(
                    "La venta se registró, pero no se recibió la dirección de la factura. Consulta el historial de facturas antes de intentar cobrar nuevamente."
                );
            }

            // Limpiar carrito
            carrito.clear();

            // Abrir automáticamente la factura
            window.location.assign(datos.url_factura);

        } catch (error) {

            console.error(
                "Error al registrar venta:",
                error
            );

            modalConfirmar.hide();

            mostrarMensaje(
                error.message ||
                "Ocurrió un error al registrar la venta.",
                "danger"
            );

        } finally {

            procesandoVenta = false;

            btnConfirmarVenta.disabled = false;

            btnConfirmarVenta.innerHTML = textoOriginal;

            renderizarPedido();
        }
    });

    renderizarPedido();

});
