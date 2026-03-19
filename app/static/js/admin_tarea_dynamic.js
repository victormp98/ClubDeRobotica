document.addEventListener('DOMContentLoaded', function() {
    // Retrasar 200ms para asegurar que Select2 de Flask-Admin se inicializó
    setTimeout(function() {
        const $proyecto = window.jQuery ? window.jQuery('#proyecto') : null;
        const $columna = window.jQuery ? window.jQuery('#columna_obj') : null;
        const $asignado = window.jQuery ? window.jQuery('#asignado') : null;

        if (!$proyecto || !$columna || $proyecto.length === 0 || $columna.length === 0) return;

        // Guardar clon original para restauraciones
        const allCols = $columna.find('option').clone();
        
        // Guardar nombres originales de usuarios para poder restaurarlos
        const allUsers = $asignado && $asignado.length > 0 ? $asignado.find('option').clone() : null;
        const originalUserTexts = {};
        if (allUsers) {
            allUsers.each(function() {
                originalUserTexts[window.jQuery(this).val()] = window.jQuery(this).text();
            });
        }

        const projectUsersCache = {};

        // Filtrado asíncrono para responsables (Requiere AJAX porque la relación es profunda)
        async function filterResponsables(proyectoId) {
            if (!$asignado || $asignado.length === 0) return;
            const currentSelected = $asignado.val();
            $asignado.empty();

            if (!proyectoId || proyectoId === '__None') {
                $asignado.append(allUsers.filter('[value="__None"], [value=""]'));
                $asignado.trigger('change');
                return;
            }

            if (!projectUsersCache[proyectoId]) {
                try {
                    const res = await fetch(`/api/admin/proyecto/${proyectoId}/users`);
                    const data = await res.json();
                    if (data.success) {
                        projectUsersCache[proyectoId] = data.users || {};
                    } else {
                        projectUsersCache[proyectoId] = {};
                    }
                } catch (e) {
                    console.error(e);
                    projectUsersCache[proyectoId] = {};
                }
            }

            const validUsersMap = projectUsersCache[proyectoId] || {};
            const validUserIds = Object.keys(validUsersMap);

            const validOptions = allUsers.filter(function() {
                const val = window.jQuery(this).val();
                if (!val || val === '__None') return true;
                return validUserIds.includes(val);
            }).clone();

            // Inyectar el cargo en el texto de cada opción válida
            validOptions.each(function() {
                const val = window.jQuery(this).val();
                if (val && val !== '__None' && validUsersMap[val]) {
                    const originalName = originalUserTexts[val] || window.jQuery(this).text();
                    window.jQuery(this).text(`${originalName} (${validUsersMap[val]})`);
                }
            });

            $asignado.append(validOptions);

            if (validOptions.filter(`[value="${currentSelected}"]`).length > 0) {
                $asignado.val(currentSelected);
            } else {
                const emptyOpt = validOptions.filter('[value="__None"], [value=""]').first();
                if (emptyOpt.length) {
                    $asignado.val(emptyOpt.val());
                } else if (validOptions.length > 0) {
                    $asignado.val(validOptions.first().val());
                }
            }
            $asignado.trigger('change');
        }

        // Filtrado síncrono para columnas utilizando texto del elemento original
        function filterColumnas() {
            const selectedProyectoId = $proyecto.val();
            const currentSelectedCol = $columna.val();
            
            $columna.empty();

            if (!selectedProyectoId || selectedProyectoId === '__None') {
                const emptyOpts = allCols.filter('[value="__None"], [value=""]');
                $columna.append(emptyOpts);
                $columna.trigger('change');
                filterResponsables(selectedProyectoId);
                return;
            }

            const validOptions = allCols.filter(function() {
                const val = window.jQuery(this).val();
                if (!val || val === '__None') return true; 
                
                const text = window.jQuery(this).text();
                // Regex mapeado desde modelo backend "__repr__" -> "(Proy: {ID})"
                const match = text.match(/\(Proy: (\d+)\)/);
                return match && match[1] === selectedProyectoId;
            });

            $columna.append(validOptions);

            if (validOptions.filter(`[value="${currentSelectedCol}"]`).length > 0) {
                $columna.val(currentSelectedCol);
            } else {
                const emptyOpt = validOptions.filter('[value="__None"], [value=""]').first();
                if (emptyOpt.length) {
                    $columna.val(emptyOpt.val());
                } else if (validOptions.length > 0) {
                    $columna.val(validOptions.first().val());
                }
            }
            $columna.trigger('change'); 
            
            // Disparar sincronizadamente el segundo filtro
            filterResponsables(selectedProyectoId);
        }

        $proyecto.on('change', filterColumnas);

        filterColumnas();
    }, 200);
});
