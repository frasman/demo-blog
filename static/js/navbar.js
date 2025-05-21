document.addEventListener("DOMContentLoaded", function () {
    function waitForElement(selector, callback, interval = 100) {
        const elementCheck = setInterval(() => {
            const element = document.querySelector(selector);
            if (element) {
                clearInterval(elementCheck);
                callback(element);
            }
        }, interval);
    }

    waitForElement(".site-mobile-menu-body", function () {
        console.log("Navbar mobile pronta");

        function siteMenuClone() {
            const jsCloneNavs = document.querySelectorAll('.js-clone-nav');
            const siteMobileMenuBody = document.querySelector('.site-mobile-menu-body');

            if (!siteMobileMenuBody || jsCloneNavs.length === 0) {
                console.error("Errore: .site-mobile-menu-body o .js-clone-nav non trovati!");
                return;
            }

            jsCloneNavs.forEach(nav => {
                const navCloned = nav.cloneNode(true);
                navCloned.classList.add('site-nav-wrap');
                siteMobileMenuBody.appendChild(navCloned);
            });

            setTimeout(() => {
                let counter = 0;
                document.querySelectorAll('.site-mobile-menu .has-children').forEach(hasChild => {
                    const refEl = hasChild.querySelector('a');
                    const newElSpan = document.createElement('span');
                    newElSpan.classList.add('arrow-collapse', 'collapsed');
                    newElSpan.setAttribute('data-toggle', 'collapse');
                    newElSpan.setAttribute('data-target', '#collapseItem' + counter);

                    hasChild.insertBefore(newElSpan, refEl);

                    const dropdown = hasChild.querySelector('.dropdown');
                    if (dropdown) {
                        dropdown.classList.add('collapse');
                        dropdown.setAttribute('id', 'collapseItem' + counter);
                    }

                    counter++;
                });
            }, 500);

            // Gestione apertura/chiusura menu mobile
            document.querySelectorAll(".js-menu-toggle").forEach(mtoggle => {
                mtoggle.addEventListener("click", (e) => {
                    e.preventDefault();
                    document.body.classList.toggle('offcanvas-menu');
                    mtoggle.classList.toggle('is-active');
                });
            });

            // Chiudere il menu quando si clicca fuori
            document.addEventListener('click', function (event) {
                const menu = document.querySelector(".site-mobile-menu");
                const isClickInside = menu && menu.contains(event.target);
                const isMenuToggle = event.target.closest(".js-menu-toggle");

                if (!isClickInside && !isMenuToggle && document.body.classList.contains('offcanvas-menu')) {
                    document.body.classList.remove('offcanvas-menu');
                    document.querySelectorAll(".js-menu-toggle").forEach(mtoggle => mtoggle.classList.remove('is-active'));
                }
            });

            // Toggle dei sottomenu
            document.addEventListener('click', function (event) {
                if (event.target.classList.contains('arrow-collapse')) {
                    event.preventDefault();
                    const target = event.target.getAttribute('data-target');
                    const dropdown = document.querySelector(target);
                    if (dropdown) {
                        dropdown.classList.toggle('show');
                        event.target.classList.toggle('collapsed');
                    }
                }
            });
        }

        siteMenuClone();
    });
});
