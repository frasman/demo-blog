document.addEventListener("DOMContentLoaded", function () {
    console.log("custom.js caricato e DOM pronto.");


    if (typeof AOS !== "undefined") {
        AOS.init({
            duration: 450,
            easing: "ease-out",
            once: true
        });
        console.log("AOS inizializzato.");
    }


    var rellaxElements = document.querySelectorAll(".rellax");
    if (rellaxElements.length > 0 && typeof Rellax !== "undefined") {
        if (window.innerWidth > 768) {
            new Rellax(".rellax");
            console.log("Rellax inizializzato.");
        } else {
            console.log("Rellax disattivato su mobile.");
        }
    }


    var preloader = function () {
        var loader = document.querySelector(".loader");
        var overlay = document.getElementById("overlayer");
        setTimeout(function () {
            loader?.classList.add("hidden");
            overlay?.classList.add("hidden");
        }, 200);
    };
    preloader();


    if (typeof tns !== "undefined") {
        var testimonialSlider = document.querySelector(".wide-slider-testimonial");
        if (testimonialSlider) {
            tns({
                container: ".wide-slider-testimonial",
                lazyLoad: true,
                items: 1,
                slideBy: 1,
                speed: 700,
                loop: true,
                autoplay: true,
                autoplayTimeout: 3500,
                autoplayHoverPause: true,
                mouseDrag: true,
                nav: true,
                controlsContainer: "#prevnext-testimonial",
                responsive: {
                    350: { items: 1 },
                    600: { items: 2 },
                    900: { items: 3 }
                }
            });
            console.log("Testimonial slider inizializzato.");
        }

        var destinationSlider = document.querySelector(".destination-slider");
        if (destinationSlider) {
            tns({
                container: ".destination-slider",
                lazyLoad: true,
                mouseDrag: true,
                items: 1,
                speed: 700,
                edgePadding: 50,
                nav: true,
                gutter: 30,
                autoplay: true,
                autoplayButtonOutput: false,
                controlsContainer: "#destination-controls",
                responsive: {
                    350: { items: 1 },
                    500: { items: 2 },
                    600: { items: 3 },
                    900: { items: 5 }
                }
            });
            console.log("Destination slider inizializzato.");
        }
    }


    if (typeof GLightbox !== "undefined" && document.querySelector(".glightbox3")) {
        GLightbox({ selector: ".glightbox3" });
        console.log("Lightbox inizializzato.");
    }


    setTimeout(function () {
        if (typeof AOS !== "undefined") {
            console.log("Aggiornamento AOS...");
            AOS.refreshHard();
        }
    }, 500);
});
