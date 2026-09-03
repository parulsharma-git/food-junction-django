/* ============================================================
   FOOD JUNCTION — SITE BEHAVIOUR
   Nav/footer are now server-rendered by Django templates.
   This handles: sticky nav shadow, mobile drawer, scroll-reveal,
   hero parallax, active nav link, and showing Django messages as toasts.
   ============================================================ */

document.addEventListener("DOMContentLoaded", () => {

  /* ---- sticky nav shadow state ---- */
  const nav = document.querySelector(".site-nav");
  const onScroll = () => {
    if (!nav) return;
    if (window.scrollY > 40) nav.classList.add("scrolled");
    else nav.classList.remove("scrolled");
  };
  document.addEventListener("scroll", onScroll, { passive:true });
  onScroll();

  /* ---- mobile menu ---- */
  const burger = document.querySelector(".nav-burger");
  const mobileMenu = document.querySelector(".mobile-menu");
  if (burger && mobileMenu){
    burger.addEventListener("click", () => {
      burger.classList.toggle("open");
      mobileMenu.classList.toggle("open");
    });
    mobileMenu.querySelectorAll("a").forEach(a=>{
      a.addEventListener("click", ()=>{ burger.classList.remove("open"); mobileMenu.classList.remove("open"); });
    });
  }

  /* ---- active nav link ---- */
  const page = (document.body.dataset.page || "").toLowerCase();
  document.querySelectorAll(".nav-links a, .mobile-menu a").forEach(a=>{
    if (a.dataset.nav === page) a.classList.add("active");
  });

  /* ---- year in footer ---- */
  const yr = document.getElementById("fjYear");
  if (yr) yr.textContent = new Date().getFullYear();

  /* ---- scroll reveal via IntersectionObserver ---- */
  const revealEls = document.querySelectorAll(".reveal, .reveal-scale");
  if ("IntersectionObserver" in window && revealEls.length){
    const io = new IntersectionObserver((entries)=>{
      entries.forEach(entry=>{
        if (entry.isIntersecting){
          entry.target.classList.add("in");
          io.unobserve(entry.target);
        }
      });
    }, { threshold:0.15, rootMargin:"0px 0px -60px 0px" });
    revealEls.forEach(el=> io.observe(el));
  } else {
    revealEls.forEach(el=> el.classList.add("in"));
  }

  /* ---- hero parallax (storytelling scroll) ---- */
  const heroCopy = document.querySelector(".hero-copy");
  const heroGrid = document.querySelector(".hero-grid");
  if (heroCopy){
    document.addEventListener("scroll", ()=>{
      const y = window.scrollY;
      if (y < window.innerHeight * 1.2){
        heroCopy.style.transform = `translateY(${y * 0.12}px)`;
        heroCopy.style.opacity = Math.max(0, 1 - y / 500);
        if (heroGrid) heroGrid.style.transform = `translateY(${y * 0.08}px)`;
      }
    }, { passive:true });
  }

  /* ---- show Django messages (from redirects) as toasts ---- */
  const msgBox = document.getElementById("djMessages");
  if (msgBox){
    const spans = msgBox.querySelectorAll("span");
    if (spans.length){
      showToast(spans[0].textContent);
    }
  }

  /* ---- veg-only checkbox on menu page: submits the filter form ---- */
  const vegToggle = document.getElementById("vegToggle");
  if (vegToggle){
    vegToggle.addEventListener("click", ()=>{
      vegToggle.closest("form").submit();
    });
  }
});

let toastTimer;
function showToast(msg){
  const t = document.getElementById("toast");
  if (!t) return;
  t.innerHTML = `<span class="dot"></span>${msg}`;
  t.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(()=> t.classList.remove("show"), 2600);
}
