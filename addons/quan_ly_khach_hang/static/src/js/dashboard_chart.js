odoo.define('dashboard_chart', function(require) {
    "use strict";

    var ajax = require('web.ajax');
    var rpc = require('web.rpc');

    console.log("📌 dashboard_chart.js đã được tải thành công!");

    $(document).ready(function () {
        console.log("Document đã sẵn sàng!");

        function loadCharts() {
            console.log("Bắt đầu loadCharts()...");

            rpc.query({
                model: 'dashboard',
                method: 'search_read',
                fields: ['so_luong_khach_bac', 'so_luong_khach_trung', 'so_luong_khach_nam',
                         'tong_chi_tieu_bac', 'tong_chi_tieu_trung', 'tong_chi_tieu_nam']
            }).then(function (data) {
                console.log("Dữ liệu trả về từ Odoo:", data);

                if (data.length === 0) {
                    console.warn("Không có dữ liệu từ Odoo!");
                    return;
                }

                var dashboardData = data[0];

                var customerData = [
                    dashboardData.so_luong_khach_bac,
                    dashboardData.so_luong_khach_trung,
                    dashboardData.so_luong_khach_nam
                ];

                var spendingData = [
                    dashboardData.tong_chi_tieu_bac,
                    dashboardData.tong_chi_tieu_trung,
                    dashboardData.tong_chi_tieu_nam
                ];

                var labels = ["Miền Bắc", "Miền Trung", "Miền Nam"];

                console.log("Dữ liệu khách hàng:", customerData);
                console.log("Dữ liệu chi tiêu:", spendingData);

                renderChart("customerChart", "Tổng số khách hàng", labels, customerData);
                renderChart("spendingChart", "Tổng chi tiêu", labels, spendingData);
            }).catch(function (error) {
                console.error("Lỗi khi gọi RPC:", error);
            });
        }

        function renderChart(canvasId, title, labels, data) {
            var canvas = document.getElementById(canvasId);
            console.log(`Kiểm tra phần tử <canvas> ${canvasId}:`, canvas);

            if (!canvas) {
                console.warn(`⚠ Không tìm thấy phần tử canvas: ${canvasId}`);
                return;
            }

            var ctx = canvas.getContext('2d');
            console.log(`🎨 Tạo biểu đồ trên ${canvasId}...`);

            new Chart(ctx, {
                type: 'pie',
                data: {
                    labels: labels,
                    datasets: [{
                        label: title,
                        data: data,
                        backgroundColor: ['#ff6384', '#36a2eb', '#ffcd56'],
                        borderColor: ['#ff6384', '#36a2eb', '#ffcd56'],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: { beginAtZero: true }
                    }
                }
            });

            console.log(`✅ Biểu đồ ${canvasId} đã được render thành công!`);
        }

        // Trì hoãn để đảm bảo view đã tải xong
        setTimeout(loadCharts, 1000);
    });
});
