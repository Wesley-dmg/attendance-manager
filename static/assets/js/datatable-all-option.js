
// Initialisation de DataTable
    $(document).ready(function() {
        $('.table').DataTable({
            paging: true,
            searching: true,
            ordering: true,
            lengthMenu: [10, 25, 50, 100],
            dom: 'Bfrtip',
            buttons: [
                {
                    extend: 'copy',
                    text: '<i class="fas fa-copy"></i> Copier',
                    exportOptions: {
                        columns: ':not(:last-child)' // Exclut la dernière colonne
                }
            },

                {
                    extend: 'excel',
                    text: '<i class="fas fa-file-excel"></i> Excel',
                    exportOptions: {
                        columns: ':not(:last-child)' // Exclut la dernière colonne
                }
            },
                {
                    extend: 'pdf',
                    text: '<i class="fas fa-file-pdf"></i> PDF',
                    exportOptions: {
                        columns: ':not(:last-child)' // Exclut la dernière colonne
                }
            },
                {
                    extend: 'print',
                    text: '<i class="fas fa-print"></i> Imprimer',
                    exportOptions: {
                        columns: ':not(:last-child)' // Exclut la dernière colonne
                }
            }
        ]
    });
});