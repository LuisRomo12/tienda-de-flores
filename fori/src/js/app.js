export default {
    mounted(el, binding) {
        const strength = binding.value?.strength || 1;

        // Contenedor necesario para mantener el flujo del DOM mientras el botón se desplaza
        // O simplemente aplicamos la transformación al propio botón con cuidado

        el.addEventListener('mousemove', (e) => {
            const rect = el.getBoundingClientRect();
            const h = rect.width / 2;
            const w = rect.height / 2;
            const x = e.clientX - rect.left - h;
            const y = e.clientY - rect.top - w;

            const multiplier = el.dataset.magneticStrength || strength;

            requestAnimationFrame(() => {
                el.style.transform = `translateX(${x * 0.4 * multiplier}px) translateY(${y * 0.4 * multiplier}px)`;
            });
        });

        el.addEventListener('mouseleave', () => {
            requestAnimationFrame(() => {
                el.style.transform = `translateX(0px) translateY(0px)`;
                // Rescatar transiciones suaves
                el.style.transition = 'transform 0.4s cubic-bezier(0.25, 0.8, 0.25, 1)';
                setTimeout(() => {
                    el.style.transition = '';
                }, 400);
            });
        });
    }
};
