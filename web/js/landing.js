(function () {
    'use strict';
    const $ = id => document.getElementById(id);
    const nav = (v) => {
        if (v === 'try') {
            window.location.href = 'dashboard.html';
            return;
        }

        if (window.__ADC_NAV__) {
            window.__ADC_NAV__(v);
            return;
        }

        // React nav bridge can appear slightly after landing scripts.
        // Retry briefly so "Try Now" still works on first click.
        let attempts = 0;
        const timer = setInterval(() => {
            attempts += 1;
            if (window.__ADC_NAV__) {
                clearInterval(timer);
                window.__ADC_NAV__(v);
            } else if (attempts >= 20) {
                clearInterval(timer);
                if (v === 'download') {
                    const download = document.getElementById('download');
                    if (download) download.scrollIntoView({ behavior: 'smooth' });
                }
            }
        }, 100);
    };

    /* ════════════ NAVBAR ════════════ */
    function initNavbar() {
        const navbar = $('navbar');
        const hamburger = $('nav-hamburger');
        const navLinks = $('nav-links');

        window.addEventListener('scroll', () => {
            navbar.classList.toggle('scrolled', window.scrollY > 40);
        });

        hamburger && hamburger.addEventListener('click', () => {
            navLinks.classList.toggle('open');
        });

        // Smooth scroll for anchor links
        document.querySelectorAll('[data-scroll]').forEach(el => {
            el.addEventListener('click', () => {
                const target = document.getElementById(el.dataset.scroll);
                if (target) target.scrollIntoView({ behavior: 'smooth' });
                navLinks.classList.remove('open');
            });
        });

        // Nav CTA
        const navCta = $('nav-cta');
        navCta && navCta.addEventListener('click', () => nav('try'));

        // Nav Try Now
        document.querySelectorAll('[data-nav]').forEach(el => {
            el.addEventListener('click', () => nav(el.dataset.nav));
        });
    }

    /* ════════════ FADE-UP OBSERVER ════════════ */
    function initScrollAnimations() {
        const io = new IntersectionObserver((entries) => {
            entries.forEach(e => {
                if (e.isIntersecting) {
                    e.target.classList.add('visible');
                    io.unobserve(e.target);
                }
            });
        }, { threshold: 0.12 });

        document.querySelectorAll('.fade-up').forEach(el => io.observe(el));
    }

    /* ════════════ COUNTER ANIMATION ════════════ */
    function animateCounters() {
        document.querySelectorAll('[data-count]').forEach(el => {
            const target = parseInt(el.dataset.count);
            const suffix = el.dataset.suffix || '';
            let current = 0;
            const step = Math.ceil(target / 60);
            const timer = setInterval(() => {
                current = Math.min(current + step, target);
                el.textContent = current.toLocaleString() + suffix;
                if (current >= target) clearInterval(timer);
            }, 25);
        });
    }

    /* ════════════ PREVIEW TABS ════════════ */
    function initPreviewTabs() {
        const tabs = document.querySelectorAll('.preview-tab');
        const screens = document.querySelectorAll('.preview-screen');

        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                tabs.forEach(t => t.classList.remove('active'));
                screens.forEach(s => s.classList.remove('active'));
                tab.classList.add('active');
                const target = document.getElementById('screen-' + tab.dataset.tab);
                if (target) target.classList.add('active');
            });
        });
    }

    /* ════════════ FAQ ACCORDION ════════════ */
    function initFAQ() {
        document.querySelectorAll('.faq-item').forEach(item => {
            const btn = item.querySelector('.faq-q');
            btn && btn.addEventListener('click', () => {
                const isOpen = item.classList.contains('open');
                document.querySelectorAll('.faq-item').forEach(i => i.classList.remove('open'));
                if (!isOpen) item.classList.add('open');
            });
        });
    }

    function initTutorials() {
        const overlay = $('video-modal');
        const titleEl = $('video-modal-title');
        const closeBtn = $('video-modal-close');

        document.querySelectorAll('[data-tutorial]').forEach(card => {
            card.addEventListener('click', () => {
                const title = card.dataset.tutorial;
                if (titleEl) titleEl.textContent = title;
                if (overlay) overlay.style.display = 'flex';
                document.body.style.overflow = 'hidden';
            });
        });

        const closeModal = () => {
            if (overlay) overlay.style.display = 'none';
            document.body.style.overflow = '';
        };

        closeBtn && closeBtn.addEventListener('click', closeModal);
        overlay && overlay.addEventListener('click', e => { if (e.target === overlay) closeModal(); });
        document.addEventListener('keydown', e => { if (e.key === 'Escape') closeModal(); });
    }

    function initParticles() {
        const canvas = $('hero-canvas');
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        let W = canvas.width = window.innerWidth;
        let H = canvas.height = window.innerHeight;

        const particles = Array.from({ length: 50 }, () => ({
            x: Math.random() * W, y: Math.random() * H,
            r: Math.random() * 1.5 + 0.5,
            dx: (Math.random() - 0.5) * 0.3,
            dy: (Math.random() - 0.5) * 0.3,
            alpha: Math.random() * 0.4 + 0.1,
        }));

        function draw() {
            ctx.clearRect(0, 0, W, H);
            particles.forEach(p => {
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(99,102,241,${p.alpha})`;
                ctx.fill();
                p.x += p.dx; p.y += p.dy;
                if (p.x < 0 || p.x > W) p.dx *= -1;
                if (p.y < 0 || p.y > H) p.dy *= -1;
            });
            requestAnimationFrame(draw);
        }
        draw();

        window.addEventListener('resize', () => {
            W = canvas.width = window.innerWidth;
            H = canvas.height = window.innerHeight;
        });
    }

    /* ════════════ TYPED HEADLINE ════════════ */
    function initTyped() {
        const el = $('typed-text');
        if (!el) return;
        const words = ['Productivity', 'Focus', 'Wellness', 'Clarity', 'Balance'];
        let wi = 0, ci = 0, deleting = false;

        function tick() {
            const word = words[wi];
            el.textContent = deleting ? word.slice(0, ci--) : word.slice(0, ci++);
            if (!deleting && ci > word.length) { deleting = true; setTimeout(tick, 1400); return; }
            if (deleting && ci < 0) { deleting = false; wi = (wi + 1) % words.length; ci = 0; }
            setTimeout(tick, deleting ? 60 : 110);
        }
        tick();
    }

    /* ════════════ INIT ════════════ */
    document.addEventListener('DOMContentLoaded', () => {
        initNavbar();
        initScrollAnimations();
        initPreviewTabs();
        initFAQ();
        initTutorials();
        initParticles();
        initTyped();

        // Counter trigger on scroll
        const statsSection = $('stats-section');
        if (statsSection) {
            const io = new IntersectionObserver(entries => {
                if (entries[0].isIntersecting) { animateCounters(); io.disconnect(); }
            }, { threshold: 0.5 });
            io.observe(statsSection);
        }
    });
})();