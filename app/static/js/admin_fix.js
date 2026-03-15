document.addEventListener('DOMContentLoaded', function() {
    // Wait a bit for Flask-Admin to render everything
    setTimeout(function() {
        const brand = document.querySelector('.navbar-brand');
        if (brand && !document.getElementById('tech-return-btn')) {
            const btn = document.createElement('a');
            btn.id = 'tech-return-btn';
            btn.href = '/';
            // Styling to match LotOS dark aesthetic
            btn.style.display = 'inline-flex';
            btn.style.alignItems = 'center';
            btn.style.gap = '8px';
            btn.style.padding = '6px 12px';
            btn.style.fontSize = '12px';
            btn.style.fontWeight = '600';
            btn.style.textTransform = 'uppercase';
            btn.style.letterSpacing = '0.5px';
            btn.style.color = '#818cf8'; // Indigo-400
            btn.style.border = '1px solid rgba(129, 140, 248, 0.3)';
            btn.style.borderRadius = '8px';
            btn.style.textDecoration = 'none';
            btn.style.marginLeft = '15px';
            btn.style.background = 'rgba(129, 140, 248, 0.05)';
            btn.style.transition = 'all 0.3s ease';
            
            btn.innerHTML = '<i class="fa fa-home"></i> Volver al Sitio';
            
            btn.onmouseover = function() {
                this.style.background = 'rgba(129, 140, 248, 0.1)';
                this.style.borderColor = 'rgba(129, 140, 248, 0.6)';
                this.style.boxShadow = '0 0 15px rgba(129, 140, 248, 0.2)';
            };
            btn.onmouseout = function() {
                this.style.background = 'rgba(129, 140, 248, 0.05)';
                this.style.borderColor = 'rgba(129, 140, 248, 0.3)';
                this.style.boxShadow = 'none';
            };
            
            brand.after(btn);
            console.log("Admin Fix: Botón 'Volver al Sitio' inyectado con éxito.");
        }
    }, 100);
});
