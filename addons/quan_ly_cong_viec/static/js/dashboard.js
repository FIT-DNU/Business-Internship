odoo.define('dashboard.progress_chart', function (require) {
    "use strict";

    var rpc = require('web.rpc');

    $(document).ready(function () {
        rpc.query({
            model: 'du_an',
            method: 'search_read',
            fields: ['ten_du_an', 'phan_tram_du_an'],
        }).then(function (result) {
            if (!result || result.length === 0) {
                console.warn("Không có dữ liệu dự án.");
                return;
            }

            var labels = result.map(proj => proj.ten_du_an);
            var data = result.map(proj => proj.phan_tram_du_an);

            var ctx = document.getElementById('progress_chart');
            if (ctx) {
                var chartContext = ctx.getContext('2d');
                new Chart(chartContext, {
                    type: 'bar',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Tiến độ (%)',
                            data: data,
                            backgroundColor: 'rgba(75, 192, 192, 0.2)',
                            borderColor: 'rgba(75, 192, 192, 1)',
                            borderWidth: 1
                        }]
                    },
                    options: {
                        scales: {
                            y: {
                                beginAtZero: true,
                                max: 100
                            }
                        }
                    }
                });
            }
        }).catch(function (error) {
            console.error("Lỗi khi tải dữ liệu dự án:", error);
        });
    });
});
