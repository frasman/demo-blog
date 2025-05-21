document.addEventListener("DOMContentLoaded", function() {
    const banner = document.getElementById('cookie-consent-banner');
    const preferenceModal = document.getElementById('cookie-preference-modal');
    const GA_TRACKING_ID = 'G-3G6CFB9BSE';

    // Controlla le preferenze salvate
    function loadPreferences() {
        const choice = localStorage.getItem('cookies-choice');
        if (choice) {
            banner.style.display = 'none'; // Nasconde il banner se l'utente ha già scelto
            document.getElementById('cookies-analytics').checked = (localStorage.getItem('cookies-analytics') === 'true') ? true : false;
            document.getElementById('cookies-marketing').checked = (localStorage.getItem('cookies-marketing') === 'true') ? true : false;
            if (localStorage.getItem('cookies-analytics') === 'true') enableGoogleAnalytics();
        } else {
            banner.style.display = 'block'; // Mostra il banner se non c'è una scelta
        }
    }

    // Accetta tutti i cookie
    document.getElementById('accept-cookies').addEventListener('click', function() {
        localStorage.setItem('cookies-choice', 'all');
        localStorage.setItem('cookies-analytics', 'true');
        localStorage.setItem('cookies-marketing', 'true');
        enableGoogleAnalytics();
        banner.style.display = 'none';
    });

    // Rifiuta tutti i cookie
    document.getElementById('decline-cookies').addEventListener('click', function() {
        localStorage.setItem('cookies-choice', 'none');
        localStorage.setItem('cookies-analytics', 'false');
        localStorage.setItem('cookies-marketing', 'false');
        banner.style.display = 'none';
    });

    // Apri il pannello delle preferenze
    document.getElementById('manage-preferences').addEventListener('click', function() {
        preferenceModal.style.display = 'block';
    });

    // Chiudi il pannello senza salvare
    document.getElementById('cancel-preferences').addEventListener('click', function() {
        preferenceModal.style.display = 'none';
    });

    // Salva le preferenze e applica le scelte
    document.getElementById('save-preferences').addEventListener('click', function() {
        const analytics = document.getElementById('cookies-analytics').checked;
        const marketing = document.getElementById('cookies-marketing').checked;

        localStorage.setItem('cookies-choice', 'custom');
        localStorage.setItem('cookies-analytics', analytics.toString());
        localStorage.setItem('cookies-marketing', marketing.toString());

        if (analytics) enableGoogleAnalytics();

        preferenceModal.style.display = 'none';
        banner.style.display = 'none';
    });

    // Funzione per attivare Google Analytics solo se il consenso è dato
    function enableGoogleAnalytics() {
        if (localStorage.getItem('cookies-analytics') === 'true') {
            const script = document.createElement('script');
            script.async = true;
            script.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA_TRACKING_ID;
            document.head.appendChild(script);

            script.onload = function() {
                window.dataLayer = window.dataLayer || [];
                function gtag(){ dataLayer.push(arguments); }
                gtag('js', new Date());
                gtag('config', GA_TRACKING_ID, { 'anonymize_ip': true });
            };
        } else {
            console.log("Google Analytics bloccato fino al consenso.");
        }
    }

    // Carica le preferenze all'avvio
    loadPreferences();
});
