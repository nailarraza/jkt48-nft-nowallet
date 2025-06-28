// D:\jkt48-nft-app\app\static\js\main.js
// File ini berisi semua JavaScript kustom untuk interaktivitas frontend.

document.addEventListener('DOMContentLoaded', function () {
    /**
     * Fungsionalitas untuk Mode Gelap/Terang (Dark/Light Mode)
     */
    const themeToggleBtns = document.querySelectorAll('#theme-toggle, #theme-toggle-mobile');
    
    // Ikon SVG untuk tombol mode
    const themeToggleDarkIcon = `<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z"></path></svg>`;
    const themeToggleLightIcon = `<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 5.05A1 1 0 003.636 6.464l.707.707a1 1 0 001.414-1.414l-.707-.707zM3 11a1 1 0 100-2H2a1 1 0 100 2h1zM6.464 16.364a1 1 0 00-1.414-1.414l-.707.707a1 1 0 001.414 1.414l.707-.707z" fill-rule="evenodd" clip-rule="evenodd"></path></svg>`;

    // Fungsi untuk menerapkan tema (menambah/menghapus class 'dark')
    function applyTheme(isDark) {
        if (isDark) {
            document.documentElement.classList.add('dark');
            themeToggleBtns.forEach(btn => btn.innerHTML = themeToggleLightIcon);
        } else {
            document.documentElement.classList.remove('dark');
            themeToggleBtns.forEach(btn => btn.innerHTML = themeToggleDarkIcon);
        }
    }

    // Cek tema yang tersimpan di localStorage atau preferensi sistem saat halaman dimuat
    const isDarkMode = localStorage.getItem('color-theme') === 'dark' || 
                      (!('color-theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches);
    applyTheme(isDarkMode);

    // Tambahkan event listener ke semua tombol ganti tema
    themeToggleBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const isCurrentlyDark = document.documentElement.classList.contains('dark');
            // Simpan preferensi tema ke localStorage
            localStorage.setItem('color-theme', isCurrentlyDark ? 'light' : 'dark');
            // Terapkan tema yang baru
            applyTheme(!isCurrentlyDark);
        });
    });


    /**
     * Fungsionalitas untuk Menu Mobile (Hamburger Menu)
     */
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');

    if (mobileMenuButton && mobileMenu) {
        mobileMenuButton.addEventListener('click', () => {
            mobileMenu.classList.toggle('hidden');
        });
    }
});
