/*
 * SCSI — comportamento mínimo do shell (Sprint 3).
 * O artefato do Design System (Duralux) fornece CSS e fontes, mas não embarca
 * seu bundle JS; este script faz apenas o toggle do menu lateral usando as
 * classes que o próprio tema espera (`html.minimenu`, `.mob-navigation-active`).
 */
(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        var miniBtn = document.getElementById('menu-mini-button');
        var mobileBtn = document.getElementById('mobile-collapse');
        var navigation = document.querySelector('.nxl-navigation');

        if (miniBtn) {
            miniBtn.addEventListener('click', function () {
                document.documentElement.classList.toggle('minimenu');
            });
        }

        if (mobileBtn && navigation) {
            mobileBtn.addEventListener('click', function () {
                navigation.classList.toggle('mob-navigation-active');
            });
        }
    });
})();
