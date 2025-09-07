// Custom JavaScript per gironi.it

$(document).ready(function() {
    // Inizializza Revolution Slider
    if ($('#slider7').length && $.fn.revolution) {
        $('#slider7').revolution({
            sliderType: "standard",
            sliderLayout: "fullwidth",
            delay: 9000,
            navigation: {
                keyboardNavigation: "off",
                keyboard_direction: "horizontal",
                mouseScrollNavigation: "off",
                onHoverStop: "off",
                touch: {
                    touchenabled: "on",
                    swipe_threshold: 75,
                    swipe_min_touches: 1,
                    swipe_direction: "horizontal",
                    drag_block_vertical: false
                },
                arrows: {
                    enable: false
                },
                bullets: {
                    enable: false
                }
            },
            responsiveLevels: [1240, 1024, 778, 480],
            gridwidth: [1240, 1024, 778, 480],
            gridheight: [800, 700, 600, 700],
            lazyType: "smart",
            parallax: {
                type: "scroll",
                origo: "slidercenter",
                speed: 400,
                levels: [5, 10, 15, 20, 25, 30, 35, 40, 45, 46, 47, 48, 49, 50, 51, 55],
                disable_onmobile: "on"
            },
            shadow: 0,
            spinner: "spinner3",
            stopLoop: "off",
            stopAfterLoops: -1,
            stopAtSlide: -1,
            shuffle: "off",
            autoHeight: "off",
            hideThumbsOnMobile: "off",
            hideSliderAtLimit: 0,
            hideCaptionAtLimit: 0,
            hideAllCaptionAtLilmit: 0,
            debugMode: false,
            fallbacks: {
                simplifyAll: "off",
                nextSlideOnWindowFocus: "off",
                disableFocusListener: false
            }
        });
    }

    // --- NUOVA GESTIONE MENU MOBILE ---
    const $hamburger = $('.navbar-hamburger .hamburger');
    const $menu = $('.navbar-collapse');

    $hamburger.on('click', function(e) {
        e.preventDefault();
        $(this).toggleClass('active');
        $menu.toggleClass('open');
    });

    // Chiudi il menu se si clicca fuori (su mobile)
    $(document).on('click', function(e) {
        // Se il menu è aperto e il click NON è sul menu E NON è sull'hamburger
        if ($menu.hasClass('open') && !$menu.is(e.target) && $menu.has(e.target).length === 0 && !$hamburger.is(e.target) && $hamburger.has(e.target).length === 0) {
            $hamburger.removeClass('active');
            $menu.removeClass('open');
        }
    });
});