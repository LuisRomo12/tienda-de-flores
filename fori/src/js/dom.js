export default {
    mounted(el, binding) {
        // binding.value puede ser un objeto con configuraciones de parallax
        const strength = binding.value?.strength || 20;

        el.dataset.initialTransform = el.style.transform || '';

        el.handleMouseMove = (e) => {
            // Calcular la posición del ratón respecto al centro de la ventana
            const x = (window.innerWidth - e.pageX * 2) / (100 / strength);
            const y = (window.innerHeight - e.pageY * 2) / (100 / strength);

            // Usar requestAnimationFrame para un rendimiento suave
            window.requestAnimationFrame(() => {
                el.style.transform = `${el.dataset.initialTransform} translateX(${x}px) translateY(${y}px)`;
            });
        };

        el.handleMouseLeave = () => {
            window.requestAnimationFrame(() => {
                el.style.transform = el.dataset.initialTransform;
                el.style.transition = 'transform 0.5s ease-out';

                // Remover la transición suave después de restaurar para no afectar el movimiento continuo
                setTimeout(() => {
                    el.style.transition = '';
                }, 500);
            });
        };

        // Añadimos el listener globalmente a la ventana para el efecto Parallax
        // (Opcionalmente, se podría atar solo al contenedor padre)
        window.addEventListener('mousemove', el.handleMouseMove);
        window.addEventListener('mouseout', el.handleMouseLeave);
    },
    unmounted(el) {
        window.removeEventListener('mousemove', el.handleMouseMove);
        window.removeEventListener('mouseout', el.handleMouseLeave);
    }
};
