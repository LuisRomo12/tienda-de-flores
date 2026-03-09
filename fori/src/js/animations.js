const observer = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
      } else {
        // Optional: Remove class when out of view to re-animate on scroll back up
        entry.target.classList.remove('is-visible');
      }
    });
  },
  {
    threshold: 0.1, // Trigger when 10% visible
    rootMargin: '0px 0px -50px 0px'
  }
);

export default {
  mounted(el, binding) {
    el.classList.add('scroll-animate');
    
    // Support staggered delay via binding.value (e.g. v-scroll="'200ms'")
    if (binding.value) {
      el.style.transitionDelay = binding.value;
    }
    
    // Check if the user passed a custom direction class, otherwise use default
    if (binding.arg) {
      el.classList.add(`scroll-animate-${binding.arg}`);
    } else {
      el.classList.add('scroll-animate-up');
    }

    observer.observe(el);
  },
  unmounted(el) {
    observer.unobserve(el);
  }
};
