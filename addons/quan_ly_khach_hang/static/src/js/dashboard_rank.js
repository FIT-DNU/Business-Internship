odoo.define('dashboard_rank', function(require) {
    "use strict";

    var rpc = require('web.rpc');

    console.log("📌 dashboard_rank.js đã được tải thành công!");

    $(document).ready(function () {
        console.log("Document đã sẵn sàng!");

        function loadRanking() {
            console.log("Bắt đầu loadRanking()...");

            rpc.query({
                model: 'bang_xep_hang_khach_hang',  // Lấy từ model xếp hạng
                method: 'search_read',
                fields: ['khach_hang_id', 'tong_tien_chi_tieu', 'xep_hang']
            }).then(function (data) {
                console.log("📊 Dữ liệu bảng xếp hạng từ Odoo:", data);

                if (data.length === 0) {
                    console.warn("⚠ Không có dữ liệu xếp hạng!");
                    return;
                }

                renderTable(data);
                renderChart(data);
            }).catch(function (error) {
                console.error("❌ Lỗi khi gọi RPC:", error);
            });
        }

        function renderTable(data) {
            var tableBody = $("#rankingTable tbody");
            tableBody.empty();

            data.forEach(function (item, index) {
                var row = `<tr>
                    <td>${item.xep_hang}</td>
                    <td>${item.khach_hang_id[1]}</td>
                    <td>${item.tong_tien_chi_tieu}</td>
                </tr>`;
                tableBody.append(row);
            });

            console.log("✅ Bảng xếp hạng đã được cập nhật!");
        }

        function renderChart(data) {
            var canvas = document.getElementById("rankingChart");
            if (!canvas) {
                console.warn("⚠ Không tìm thấy phần tử canvas!");
                return;
            }

            var ctx = canvas.getContext('2d');

            // Chuẩn bị dữ liệu
            var labels = data.map(item => item.khach_hang_id[1]);  // Tên khách hàng
            var totalSpending = data.map(item => item.tong_tien_chi_tieu);  // Tổng chi tiêu

            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: "Tổng tiền chi tiêu",
                        data: totalSpending,
                        backgroundColor: 'rgba(54, 162, 235, 0.6)',
                        borderColor: 'rgba(54, 162, 235, 1)',
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

            console.log("✅ Biểu đồ bảng xếp hạng đã được tạo!");
        }

        setTimeout(loadRanking, 1000);
    });
});
