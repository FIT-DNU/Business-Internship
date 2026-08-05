odoo.define('thong_ke_ho_tro', function(require) {
    "use strict";

    var rpc = require('web.rpc');

    console.log("📌 thong_ke_ho_tro.js đã được tải thành công!");

    $(document).ready(function () {
        console.log("Document đã sẵn sàng!");

        function loadSupportStats() {
            console.log("Bắt đầu loadSupportStats()...");

            rpc.query({
                model: 'thong_ke_ho_tro_nhan_vien',
                method: 'search_read',
                fields: ['nhan_vien_id', 'so_lan_ho_tro']
            }).then(function (data) {
                console.log("📊 Dữ liệu thống kê từ Odoo:", data);

                if (data.length === 0) {
                    console.warn("⚠ Không có dữ liệu thống kê!");
                    return;
                }

                renderTable(data);
                renderChart(data);
            }).catch(function (error) {
                console.error("❌ Lỗi khi gọi RPC:", error);
            });
        }

        function renderTable(data) {
            var tableBody = $("#supportStatsTable tbody");
            tableBody.empty();

            data.forEach(function (item) {
                var row = `<tr>
                    <td>${item.nhan_vien_id[1]}</td>
                    <td>${item.so_lan_ho_tro}</td>
                </tr>`;
                tableBody.append(row);
            });

            console.log("✅ Bảng thống kê đã được cập nhật!");
        }

        function renderChart(data) {
            var canvas = document.getElementById("supportChart");
            if (!canvas) {
                console.warn("⚠ Không tìm thấy phần tử canvas!");
                return;
            }

            var ctx = canvas.getContext('2d');

            var labels = data.map(item => item.nhan_vien_id[1]);  // Tên nhân viên
            var supportCounts = data.map(item => item.so_lan_ho_tro);  // Số lần hỗ trợ

            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: "Số lần hỗ trợ",
                        data: supportCounts,
                        backgroundColor: 'rgba(255, 99, 132, 0.6)',
                        borderColor: 'rgba(255, 99, 132, 1)',
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

            console.log("✅ Biểu đồ thống kê hỗ trợ đã được tạo!");
        }

        setTimeout(loadSupportStats, 1000);
    });
});
