const FitApp = {
    state: {
        data: null,
        currentModule: "work",
        currentPage: "work_overview",
        expanded: {
            hr: false,
            project: false,
            work: true,
        },
        query: "",
    },

    async rpc(route, params = {}) {
        const response = await fetch(route, {
            method: "POST",
            credentials: "same-origin",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                jsonrpc: "2.0",
                method: "call",
                params,
                id: Date.now(),
            }),
        });

        const payload = await response.json();

        if (payload.error) {
            throw new Error(payload.error.data?.message || payload.error.message || "RPC error");
        }

        return payload.result;
    },

    escape(value) {
        return String(value ?? "")
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#039;");
    },

    toast(message) {
        const toast = document.querySelector(".fit-toast");
        if (!toast) return;

        toast.textContent = message;
        toast.classList.add("show");

        setTimeout(() => toast.classList.remove("show"), 2500);
    },

    async load() {
        document.getElementById("fit-root").innerHTML = `
            <div class="fit-loading-screen">Đang tải dữ liệu từ Odoo...</div>
        `;

        try {
            this.state.data = await this.rpc("/fit/api/bootstrap");
            this.render();
        } catch (error) {
            document.getElementById("fit-root").innerHTML = `
                <div style="padding:24px">
                    <h2>Không tải được frontend</h2>
                    <p>${this.escape(error.message)}</p>
                </div>
            `;
        }
    },

    render() {
        document.getElementById("fit-root").innerHTML = `
            <div class="fit-app">
                <aside class="fit-sidebar">
                    ${this.renderBrand()}
                    ${this.renderSidebar()}
                    ${this.renderQuickStats()}
                </aside>

                <main class="fit-main">
                    ${this.renderTopbar()}
                    <div class="js-main-content">
                        ${this.renderMainContent()}
                    </div>
                </main>
            </div>

            ${this.createTaskModal()}
            ${this.createWorkLogModal()}
            ${this.createEvaluationModal()}
            <div class="fit-toast"></div>
        `;

        this.bindEvents();
    },

    bindEvents() {
        const root = document.getElementById("fit-root");

        root.onclick = (event) => {
            const moduleEl = event.target.closest("[data-module]");
            if (moduleEl) {
                event.preventDefault();
                event.stopPropagation();
                this.toggleModule(moduleEl.dataset.module);
                return;
            }

            const pageEl = event.target.closest("[data-page]");
            if (pageEl) {
                event.preventDefault();
                event.stopPropagation();
                this.setPage(pageEl.dataset.page);
                return;
            }

            const actionEl = event.target.closest("[data-action]");
            if (actionEl) {
                event.preventDefault();
                event.stopPropagation();
                this.handleAction(actionEl.dataset.action, actionEl.dataset);
            }
        };

        root.oninput = (event) => {
            if (event.target.classList.contains("fit-search")) {
                this.state.query = event.target.value.toLowerCase();
                this.renderMainOnly();
            }
        };
    },

    handleAction(action, dataset) {
        const actions = {
            refresh: () => this.load(),

            openTaskModal: () => this.openModal("task-modal"),
            createTask: () => this.createTask(),

            openWorkLogModal: () => this.openModal("work-log-modal"),
            createWorkLog: () => this.createWorkLog(),

            openEvaluationModal: () => this.openModal("evaluation-modal"),
            createEvaluation: () => this.createEvaluation(),

            closeModal: () => this.closeModal(dataset.modal),

            taskNotStarted: () => this.updateTaskStatus(Number(dataset.id), "not_started"),
            taskInProgress: () => this.updateTaskStatus(Number(dataset.id), "in_progress"),
            taskCompleted: () => this.updateTaskStatus(Number(dataset.id), "completed"),
            taskDelayed: () => this.updateTaskStatus(Number(dataset.id), "delayed"),

            projectInProgress: () => this.updateProjectStatus(Number(dataset.id), "dang_thuc_hien"),
            projectCompleted: () => this.updateProjectStatus(Number(dataset.id), "hoan_thanh"),
            projectPaused: () => this.updateProjectStatus(Number(dataset.id), "tam_dung"),

            createProject: () => this.createProjectPrompt(),
            createStage: () => this.createStagePrompt(),
            createBudget: () => this.createBudgetPrompt(),
            createExpense: () => this.createExpensePrompt(),
            createResource: () => this.createResourcePrompt(),

            aiGenerateTasks: () => this.aiGenerateTasks(),
            aiGenerateForProject: () => this.aiGenerateTasks(Number(dataset.id)),

            createEmployee: () => this.createEmployeePrompt(),
            createPosition: () => this.createPositionPrompt(),
            createDepartment: () => this.createDepartmentPrompt(),
            createTeam: () => this.createTeamPrompt(),
            createHistory: () => this.createHistoryPrompt(),
        };

        if (actions[action]) {
            actions[action]();
        }
    },

    setPage(page) {
        this.state.currentPage = page;

        if (page.startsWith("work_")) {
            this.state.currentModule = "work";
            this.state.expanded.work = true;
        }

        if (page.startsWith("project_")) {
            this.state.currentModule = "project";
            this.state.expanded.project = true;
        }

        if (page.startsWith("hr_")) {
            this.state.currentModule = "hr";
            this.state.expanded.hr = true;
        }

        this.render();
    },

    toggleModule(moduleName) {
        const willOpen = !this.state.expanded[moduleName];

        this.state.currentModule = moduleName;
        this.state.expanded[moduleName] = willOpen;

        if (willOpen) {
            if (moduleName === "hr" && !String(this.state.currentPage).startsWith("hr_")) {
                this.state.currentPage = "hr_overview";
            }

            if (moduleName === "project" && !String(this.state.currentPage).startsWith("project_")) {
                this.state.currentPage = "project_overview";
            }

            if (moduleName === "work" && !String(this.state.currentPage).startsWith("work_")) {
                this.state.currentPage = "work_overview";
            }
        }

        this.render();
    },

    moduleClass(moduleName) {
        return this.state.currentModule === moduleName ? "active" : "";
    },

    pageClass(page) {
        return this.state.currentPage === page ? "active" : "";
    },

    renderBrand() {
        return `
            <div class="fit-brand">
                <div class="fit-brand-icon">▦</div>
                <div>
                    <div class="fit-brand-title">Dashboard</div>
                    <div class="fit-brand-sub">Project Workspace</div>
                </div>
            </div>
        `;
    },

    renderSidebar() {
        return `
            <div class="fit-nav">
                <div class="fit-nav-item ${this.pageClass("work_overview")}" data-page="work_overview">
                    <span>⌂ Tổng quan</span>
                </div>

                <div class="fit-nav-title">Quản lý</div>

                <div class="fit-nav-group">
                    <div class="fit-nav-item ${this.moduleClass("hr")}" data-module="hr">
                        <span>👥 Quản lý nhân sự</span>
                        <b>${this.state.expanded.hr ? "⌃" : "⌄"}</b>
                    </div>

                    ${this.state.expanded.hr ? `
                        <div class="fit-submenu">
                            <div class="${this.pageClass("hr_overview")}" data-page="hr_overview">Tổng quan nhân sự</div>
                            <div class="${this.pageClass("hr_employees")}" data-page="hr_employees">Nhân viên</div>
                            <div class="${this.pageClass("hr_positions")}" data-page="hr_positions">Chức vụ</div>
                            <div class="${this.pageClass("hr_departments")}" data-page="hr_departments">Phòng ban</div>
                            <div class="${this.pageClass("hr_teams")}" data-page="hr_teams">Nhóm dự án</div>
                            <div class="${this.pageClass("hr_histories")}" data-page="hr_histories">Lịch sử làm việc</div>
                        </div>
                    ` : ""}
                </div>

                <div class="fit-nav-group">
                    <div class="fit-nav-item ${this.moduleClass("project")}" data-module="project">
                        <span>📁 Quản lý dự án</span>
                        <b>${this.state.expanded.project ? "⌃" : "⌄"}</b>
                    </div>

                    ${this.state.expanded.project ? `
                        <div class="fit-submenu">
                            <div class="${this.pageClass("project_overview")}" data-page="project_overview">Tổng quan dự án</div>
                            <div class="${this.pageClass("project_projects")}" data-page="project_projects">Dự án</div>
                            <div class="${this.pageClass("project_stages")}" data-page="project_stages">Giai đoạn</div>
                            <div class="${this.pageClass("project_budgets")}" data-page="project_budgets">Ngân sách</div>
                            <div class="${this.pageClass("project_expenses")}" data-page="project_expenses">Chi phí</div>
                            <div class="${this.pageClass("project_resources")}" data-page="project_resources">Tài nguyên</div>
                        </div>
                    ` : ""}
                </div>

                <div class="fit-nav-group">
                    <div class="fit-nav-item ${this.moduleClass("work")}" data-module="work">
                        <span>☷ Quản lý công việc</span>
                        <b>${this.state.expanded.work ? "⌃" : "⌄"}</b>
                    </div>

                    ${this.state.expanded.work ? `
                        <div class="fit-submenu">
                            <div class="${this.pageClass("work_overview")}" data-page="work_overview">Tổng quan công việc</div>
                            <div class="${this.pageClass("work_tasks")}" data-page="work_tasks">Công việc</div>
                            <div class="${this.pageClass("work_logs")}" data-page="work_logs">Nhật ký công việc</div>
                            <div class="${this.pageClass("work_evaluations")}" data-page="work_evaluations">Đánh giá nhân viên</div>
                        </div>
                    ` : ""}
                </div>
            </div>
        `;
    },

    renderQuickStats() {
        if (this.state.currentModule === "hr") {
            const stats = this.state.data.hr.stats;

            return `
                <div class="fit-mini">
                    <h3>Tổng quan nhân sự</h3>
                    <div><strong>${stats.employees}</strong><span>Nhân viên</span></div>
                    <div><strong>${stats.departments}</strong><span>Phòng ban</span></div>
                    <div><strong>${stats.positions}</strong><span>Chức vụ</span></div>
                    <div><strong>${stats.teams}</strong><span>Nhóm dự án</span></div>
                </div>
            `;
        }

        if (this.state.currentModule === "project") {
            const stats = this.state.data.project.stats;

            return `
                <div class="fit-mini">
                    <h3>Tổng quan dự án</h3>
                    <div><strong>${stats.total}</strong><span>Dự án</span></div>
                    <div><strong>${stats.completed}</strong><span>Hoàn thành</span></div>
                    <div><strong>${stats.budgets}</strong><span>Ngân sách</span></div>
                    <div><strong>${stats.expenses}</strong><span>Chi phí</span></div>
                </div>
            `;
        }

        const stats = this.state.data.work.stats;

        return `
            <div class="fit-mini">
                <h3>Tổng quan công việc</h3>
                <div><strong>${stats.total}</strong><span>Công việc</span></div>
                <div><strong>${stats.in_progress}</strong><span>Đang làm</span></div>
                <div><strong>${stats.logs}</strong><span>Nhật ký</span></div>
                <div><strong>${stats.evaluations}</strong><span>Đánh giá</span></div>
            </div>
        `;
    },

    renderTopbar() {
        const titles = {
            work_overview: "Tổng quan công việc",
            work_tasks: "Công việc",
            work_logs: "Nhật ký công việc",
            work_evaluations: "Đánh giá nhân viên",

            project_overview: "Tổng quan dự án",
            project_projects: "Dự án",
            project_stages: "Giai đoạn",
            project_budgets: "Ngân sách",
            project_expenses: "Chi phí",
            project_resources: "Tài nguyên",

            hr_overview: "Tổng quan nhân sự",
            hr_employees: "Nhân viên",
            hr_positions: "Chức vụ",
            hr_departments: "Phòng ban",
            hr_teams: "Nhóm dự án",
            hr_histories: "Lịch sử làm việc",
        };

        return `
            <header class="fit-top">
                <div>
                    <h1>${this.escape(titles[this.state.currentPage] || "Dashboard")} 👋</h1>
                    <p>Xin chào ${this.escape(this.state.data.user.name)} — thao tác dữ liệu trực tiếp qua API Odoo</p>
                </div>

                <div class="fit-actions">
                    <input class="fit-search" value="${this.escape(this.state.query)}" placeholder="Tìm kiếm công việc, dự án, nhân sự..." />
                    <button class="fit-btn" data-action="refresh">⟳ Làm mới</button>
                    ${this.renderPrimaryAction()}
                </div>
            </header>
        `;
    },

    renderPrimaryAction() {
        const page = this.state.currentPage;

        if (page === "work_logs") {
            return `<button class="fit-btn primary" data-action="openWorkLogModal">+ Tạo nhật ký</button>`;
        }

        if (page === "work_evaluations") {
            return `<button class="fit-btn primary" data-action="openEvaluationModal">+ Tạo đánh giá</button>`;
        }

        if (page === "project_projects") {
            return `<button class="fit-btn primary" data-action="createProject">+ Tạo dự án</button>`;
        }

        if (page === "project_stages") {
            return `<button class="fit-btn primary" data-action="createStage">+ Tạo giai đoạn</button>`;
        }

        if (page === "project_budgets") {
            return `<button class="fit-btn primary" data-action="createBudget">+ Tạo ngân sách</button>`;
        }

        if (page === "project_expenses") {
            return `<button class="fit-btn primary" data-action="createExpense">+ Tạo chi phí</button>`;
        }

        if (page === "project_resources") {
            return `<button class="fit-btn primary" data-action="createResource">+ Tạo tài nguyên</button>`;
        }

        if (page === "hr_employees") {
            return `<button class="fit-btn primary" data-action="createEmployee">+ Tạo nhân viên</button>`;
        }

        if (page === "hr_positions") {
            return `<button class="fit-btn primary" data-action="createPosition">+ Tạo chức vụ</button>`;
        }

        if (page === "hr_departments") {
            return `<button class="fit-btn primary" data-action="createDepartment">+ Tạo phòng ban</button>`;
        }

        if (page === "hr_teams") {
            return `<button class="fit-btn primary" data-action="createTeam">+ Tạo nhóm</button>`;
        }

        if (page === "hr_histories") {
            return `<button class="fit-btn primary" data-action="createHistory">+ Tạo lịch sử</button>`;
        }

        return "";
    },

    renderMainOnly() {
        const main = document.querySelector(".fit-main");
        if (!main) return;

        main.innerHTML = `
            ${this.renderTopbar()}
            <div class="js-main-content">
                ${this.renderMainContent()}
            </div>
        `;
    },

    renderMainContent() {
        const page = this.state.currentPage;

        if (page === "work_tasks") return this.renderWorkTasksPage();
        if (page === "work_logs") return this.renderWorkLogsPage();
        if (page === "work_evaluations") return this.renderEvaluationsPage();

        if (page === "project_overview") return this.renderProjectOverviewPage();
        if (page === "project_projects") return this.renderProjectProjectsPage();
        if (page === "project_stages") return this.renderProjectStagesPage();
        if (page === "project_budgets") return this.renderProjectBudgetsPage();
        if (page === "project_expenses") return this.renderProjectExpensesPage();
        if (page === "project_resources") return this.renderProjectResourcesPage();

        if (page === "hr_overview") return this.renderHROverviewPage();
        if (page === "hr_employees") return this.renderHREmployeesPage();
        if (page === "hr_positions") return this.renderHRPositionsPage();
        if (page === "hr_departments") return this.renderHRDepartmentsPage();
        if (page === "hr_teams") return this.renderHRTeamsPage();
        if (page === "hr_histories") return this.renderHRHistoriesPage();

        return this.renderWorkOverviewPage();
    },

    renderWorkOverviewPage() {
        const work = this.state.data.work;
        const stats = work.stats;

        return `
            <section class="fit-stats">
                ${this.statCard("purple", "☷", "Tổng công việc", stats.total, `${stats.projects} dự án`)}
                ${this.statCard("blue", "▷", "Đang thực hiện", stats.in_progress, `${stats.in_progress_percent}%`)}
                ${this.statCard("orange", "◷", "Chưa bắt đầu", stats.not_started, `${stats.not_started_percent}%`)}
                ${this.statCard("green", "✓", "Hoàn thành", stats.completed, `${stats.completed_percent}%`)}
                ${this.statCard("red", "Ⅱ", "Trì hoãn", stats.delayed, `${stats.delayed_percent}%`)}
            </section>

            <section class="fit-layout">
                <div class="fit-board-wrap">
                    <div class="fit-toolbar">
                        <div class="fit-tabs">
                            <button class="fit-tab active">▦ Bảng công việc</button>
                            <button class="fit-tab" data-page="work_tasks">☷ Danh sách</button>
                            <button class="fit-tab" data-page="work_logs">◴ Nhật ký</button>
                        </div>
                    </div>

                    <div class="fit-board">
                        ${work.columns.map(column => this.column(column)).join("")}
                    </div>
                </div>

                <aside class="fit-right">
                    <div class="fit-panel">
                        <h3>Lịch / Công việc sắp đến hạn</h3>
                        ${work.upcoming_tasks.map(task => this.upcoming(task)).join("")}
                    </div>

                    <div class="fit-panel">
                        <h3>Nhật ký gần đây</h3>
                        ${work.logs.slice(0, 6).map(log => this.smallLog(log)).join("")}
                    </div>
                </aside>
            </section>
        `;
    },

    renderWorkTasksPage() {
        const tasks = this.filterItems(this.state.data.work.tasks, ["name", "code", "project", "responsible", "status_label", "priority_label"]);

        return this.renderTablePage(
            "Danh sách công việc",
            "Quản lý công việc, trạng thái, tiến độ và người phụ trách",
            "+ Tạo công việc thủ công",
            "openTaskModal",
            ["Mã", "Tên công việc", "Dự án", "Phụ trách", "Ưu tiên", "Trạng thái", "Tiến độ", "Hạn chót", "Thao tác"],
            tasks.map(task => `
                <tr>
                    <td>${this.escape(task.code)}</td>
                    <td><b>${this.escape(task.name)}</b></td>
                    <td>${this.escape(task.project)}</td>
                    <td>${this.escape(task.responsible || "Chưa có")}</td>
                    <td><span class="fit-badge priority-${this.escape(task.priority)}">${this.escape(task.priority_label)}</span></td>
                    <td><span class="fit-badge status-${this.escape(task.status)}">${this.escape(task.status_label)}</span></td>
                    <td>${task.progress}%</td>
                    <td>${this.escape(task.deadline || "Chưa có")}</td>
                    <td>
                        <button class="fit-mini-btn" data-action="taskInProgress" data-id="${task.id}">Đang làm</button>
                        <button class="fit-mini-btn" data-action="taskCompleted" data-id="${task.id}">Hoàn thành</button>
                    </td>
                </tr>
            `).join("")
        );
    },

    renderWorkLogsPage() {
        const logs = this.filterItems(this.state.data.work.logs, ["name", "task", "project", "employees", "state_label", "description"]);

        return this.renderTablePage(
            "Nhật ký công việc",
            "Theo dõi mức độ hoàn thành và lịch sử thực hiện công việc",
            "+ Tạo nhật ký",
            "openWorkLogModal",
            ["Ngày", "Công việc", "Dự án", "Người thực hiện", "Mức độ", "Trạng thái", "Mô tả"],
            logs.map(log => `
                <tr>
                    <td>${this.escape(log.date)}</td>
                    <td><b>${this.escape(log.task)}</b></td>
                    <td>${this.escape(log.project)}</td>
                    <td>${this.escape(log.employees || "Chưa có")}</td>
                    <td>${log.progress}%</td>
                    <td>${this.escape(log.state_label)}</td>
                    <td>${this.escape(log.description)}</td>
                </tr>
            `).join("")
        );
    },

    renderEvaluationsPage() {
        const items = this.filterItems(this.state.data.work.evaluations, ["employee", "task", "project", "score", "comment"]);

        return this.renderTablePage(
            "Đánh giá nhân viên",
            "Đánh giá nhân sự theo công việc hoặc dự án",
            "+ Tạo đánh giá",
            "openEvaluationModal",
            ["Ngày", "Nhân viên", "Công việc", "Dự án", "Điểm", "Nhận xét"],
            items.map(item => `
                <tr>
                    <td>${this.escape(item.date)}</td>
                    <td><b>${this.escape(item.employee)}</b></td>
                    <td>${this.escape(item.task || "Không gắn công việc")}</td>
                    <td>${this.escape(item.project || "Không gắn dự án")}</td>
                    <td><span class="fit-score">${this.escape(item.score)}</span></td>
                    <td>${this.escape(item.comment)}</td>
                </tr>
            `).join("")
        );
    },

    renderProjectOverviewPage() {
        const project = this.state.data.project;
        const stats = project.stats;

        return `
            <section class="fit-stats">
                ${this.statCard("purple", "📁", "Tổng dự án", stats.total, `${stats.stages} giai đoạn`)}
                ${this.statCard("blue", "▷", "Đang thực hiện", stats.in_progress, "Dự án đang chạy")}
                ${this.statCard("green", "✓", "Hoàn thành", stats.completed, "Dự án hoàn tất")}
                ${this.statCard("orange", "💰", "Ngân sách", this.formatMoney(stats.total_budget), `Đã chi ${this.formatMoney(stats.total_spent)}`)}
                ${this.statCard("red", "🧾", "Chi phí", stats.expenses, `${stats.resources} tài nguyên`)}
            </section>

            <section class="fit-layout">
                <div class="fit-board-wrap">
                    <div class="fit-toolbar">
                        <div class="fit-tabs">
                            <button class="fit-tab active">▦ Tổng quan</button>
                            <button class="fit-tab" data-page="project_projects">📁 Dự án</button>
                            <button class="fit-tab" data-page="project_budgets">💰 Ngân sách</button>
                            <button class="fit-tab" data-page="project_expenses">🧾 Chi phí</button>
                        </div>
                    </div>

                    <div class="fit-project-grid">
                        ${project.projects.map(p => this.projectCard(p)).join("")}
                    </div>
                </div>

                <aside class="fit-right">
                    <div class="fit-panel">
                        <h3>Ngân sách gần đây</h3>
                        ${project.budgets.slice(0, 6).map(b => `
                            <div class="fit-upcoming">
                                <b>${this.escape(b.name)}</b>
                                <span>${this.escape(b.project)}</span>
                                <small>Dự toán: ${this.formatMoney(b.planned)} — Đã chi: ${this.formatMoney(b.spent)}</small>
                            </div>
                        `).join("")}
                    </div>
                </aside>
            </section>
        `;
    },

    renderProjectProjectsPage() {
        const items = this.filterItems(this.state.data.project.projects, ["name", "code", "responsible", "status_label", "employee_names"]);

        return this.renderTablePage(
            "Dự án",
            "Quản lý danh sách dự án, trạng thái, tiến độ và nhân sự tham gia",
            "+ Tạo dự án",
            "createProject",
            ["Mã", "Tên dự án", "Phụ trách", "Nhân viên", "Trạng thái", "Tiến độ", "Thao tác"],
            items.map(p => `
                <tr>
                    <td>${this.escape(p.code)}</td>
                    <td><b>${this.escape(p.name)}</b></td>
                    <td>${this.escape(p.responsible || "Chưa có")}</td>
                    <td>${this.escape(p.employee_count)}</td>
                    <td><span class="fit-badge status-${this.escape(p.status)}">${this.escape(p.status_label)}</span></td>
                    <td>${p.progress}%</td>
                    <td>
                        <button class="fit-mini-btn" data-action="aiGenerateForProject" data-id="${p.id}">✨ AI</button>
                        <button class="fit-mini-btn" data-action="projectInProgress" data-id="${p.id}">Đang chạy</button>
                        <button class="fit-mini-btn" data-action="projectCompleted" data-id="${p.id}">Hoàn thành</button>
                        <button class="fit-mini-btn" data-action="projectPaused" data-id="${p.id}">Tạm dừng</button>
                    </td>
                </tr>
            `).join("")
        );
    },

    renderProjectStagesPage() {
        const items = this.filterItems(this.state.data.project.stages, ["name", "project", "description"]);

        return this.renderTablePage(
            "Giai đoạn",
            "Các giai đoạn công việc thuộc từng dự án",
            "+ Tạo giai đoạn",
            "createStage",
            ["Thứ tự", "Tên giai đoạn", "Dự án", "Mô tả"],
            items.map(s => `
                <tr>
                    <td>${s.order}</td>
                    <td><b>${this.escape(s.name)}</b></td>
                    <td>${this.escape(s.project)}</td>
                    <td>${this.escape(s.description)}</td>
                </tr>
            `).join("")
        );
    },

    renderProjectBudgetsPage() {
        const items = this.filterItems(this.state.data.project.budgets, ["code", "name", "project"]);

        return this.renderTablePage(
            "Ngân sách",
            "Quản lý ngân sách dự toán, phân bổ, dự trù và chi phí thực tế",
            "+ Tạo ngân sách",
            "createBudget",
            ["Mã", "Tên ngân sách", "Dự án", "Dự toán", "Phân bổ", "Dự trù", "Đã chi", "Chênh lệch"],
            items.map(b => `
                <tr>
                    <td>${this.escape(b.code)}</td>
                    <td><b>${this.escape(b.name)}</b></td>
                    <td>${this.escape(b.project)}</td>
                    <td>${this.formatMoney(b.planned)}</td>
                    <td>${this.formatMoney(b.allocated)}</td>
                    <td>${this.formatMoney(b.reserved)}</td>
                    <td>${this.formatMoney(b.spent)}</td>
                    <td>${this.formatMoney(b.difference)}</td>
                </tr>
            `).join("")
        );
    },

    renderProjectExpensesPage() {
        const items = this.filterItems(this.state.data.project.expenses, ["name", "budget", "project", "task", "description"]);

        return this.renderTablePage(
            "Chi phí",
            "Theo dõi chi phí thực tế theo ngân sách và dự án",
            "+ Tạo chi phí",
            "createExpense",
            ["Ngày", "Khoản chi", "Ngân sách", "Dự án", "Công việc", "Số tiền", "Mô tả"],
            items.map(e => `
                <tr>
                    <td>${this.escape(e.date)}</td>
                    <td><b>${this.escape(e.name)}</b></td>
                    <td>${this.escape(e.budget)}</td>
                    <td>${this.escape(e.project)}</td>
                    <td>${this.escape(e.task || "Không gắn")}</td>
                    <td>${this.formatMoney(e.amount)}</td>
                    <td>${this.escape(e.description)}</td>
                </tr>
            `).join("")
        );
    },

    renderProjectResourcesPage() {
        const items = this.filterItems(this.state.data.project.resources, ["name", "project", "unit", "description"]);

        return this.renderTablePage(
            "Tài nguyên",
            "Quản lý tài nguyên được dùng cho từng dự án",
            "+ Tạo tài nguyên",
            "createResource",
            ["Tên tài nguyên", "Dự án", "Số lượng", "Đơn vị", "Mô tả"],
            items.map(r => `
                <tr>
                    <td><b>${this.escape(r.name)}</b></td>
                    <td>${this.escape(r.project)}</td>
                    <td>${this.escape(r.quantity)}</td>
                    <td>${this.escape(r.unit)}</td>
                    <td>${this.escape(r.description)}</td>
                </tr>
            `).join("")
        );
    },

    renderHROverviewPage() {
        const hr = this.state.data.hr;
        const stats = hr.stats;

        return `
            <section class="fit-stats">
                ${this.statCard("purple", "👥", "Nhân viên", stats.employees, `${stats.male} nam / ${stats.female} nữ`)}
                ${this.statCard("blue", "🏢", "Phòng ban", stats.departments, "Đơn vị tổ chức")}
                ${this.statCard("orange", "💼", "Chức vụ", stats.positions, "Vai trò nhân sự")}
                ${this.statCard("green", "👨‍👩‍👧", "Nhóm dự án", stats.teams, "Nhóm làm việc")}
                ${this.statCard("red", "🕘", "Lịch sử", stats.histories, "Lịch sử làm việc")}
            </section>

            <section class="fit-layout">
                <div class="fit-board-wrap">
                    <div class="fit-toolbar">
                        <div class="fit-tabs">
                            <button class="fit-tab active">▦ Tổng quan</button>
                            <button class="fit-tab" data-page="hr_employees">👥 Nhân viên</button>
                            <button class="fit-tab" data-page="hr_departments">🏢 Phòng ban</button>
                            <button class="fit-tab" data-page="hr_positions">💼 Chức vụ</button>
                        </div>
                    </div>

                    <div class="fit-project-grid">
                        ${hr.employees.slice(0, 12).map(e => this.employeeCard(e)).join("")}
                    </div>
                </div>

                <aside class="fit-right">
                    <div class="fit-panel">
                        <h3>Phòng ban</h3>
                        ${hr.departments.slice(0, 8).map(d => `
                            <div class="fit-upcoming">
                                <b>${this.escape(d.name)}</b>
                                <span>${this.escape(d.code)}</span>
                                <small>${d.employee_count} nhân viên</small>
                            </div>
                        `).join("")}
                    </div>
                </aside>
            </section>
        `;
    },

    renderHREmployeesPage() {
        const items = this.filterItems(this.state.data.hr.employees, ["code", "name", "email", "phone", "position", "department", "gender_label"]);

        return this.renderTablePage(
            "Nhân viên",
            "Quản lý hồ sơ nhân viên, phòng ban và chức vụ",
            "+ Tạo nhân viên",
            "createEmployee",
            ["Mã", "Họ và tên", "Giới tính", "Email", "SĐT", "Chức vụ", "Phòng ban", "Nhóm dự án"],
            items.map(e => `
                <tr>
                    <td>${this.escape(e.code)}</td>
                    <td><b>${this.escape(e.name)}</b></td>
                    <td>${this.escape(e.gender_label)}</td>
                    <td>${this.escape(e.email)}</td>
                    <td>${this.escape(e.phone)}</td>
                    <td>${this.escape(e.position)}</td>
                    <td>${this.escape(e.department)}</td>
                    <td>${this.escape(e.team_names)}</td>
                </tr>
            `).join("")
        );
    },

    renderHRPositionsPage() {
        const items = this.filterItems(this.state.data.hr.positions, ["code", "name", "description"]);

        return this.renderTablePage(
            "Chức vụ",
            "Danh sách chức vụ và số nhân viên đang đảm nhiệm",
            "+ Tạo chức vụ",
            "createPosition",
            ["Mã", "Tên chức vụ", "Số nhân viên", "Mô tả"],
            items.map(p => `
                <tr>
                    <td>${this.escape(p.code)}</td>
                    <td><b>${this.escape(p.name)}</b></td>
                    <td>${p.employee_count}</td>
                    <td>${this.escape(p.description)}</td>
                </tr>
            `).join("")
        );
    },

    renderHRDepartmentsPage() {
        const items = this.filterItems(this.state.data.hr.departments, ["code", "name", "description"]);

        return this.renderTablePage(
            "Phòng ban",
            "Danh sách phòng ban và số nhân viên trực thuộc",
            "+ Tạo phòng ban",
            "createDepartment",
            ["Mã", "Tên phòng ban", "Số nhân viên", "Mô tả"],
            items.map(d => `
                <tr>
                    <td>${this.escape(d.code)}</td>
                    <td><b>${this.escape(d.name)}</b></td>
                    <td>${d.employee_count}</td>
                    <td>${this.escape(d.description)}</td>
                </tr>
            `).join("")
        );
    },

    renderHRTeamsPage() {
        const items = this.filterItems(this.state.data.hr.teams, ["name", "description", "employees"]);

        return this.renderTablePage(
            "Nhóm dự án",
            "Quản lý nhóm dự án và thành viên tham gia",
            "+ Tạo nhóm",
            "createTeam",
            ["Tên nhóm", "Số thành viên", "Thành viên", "Mô tả"],
            items.map(t => `
                <tr>
                    <td><b>${this.escape(t.name)}</b></td>
                    <td>${t.employee_count}</td>
                    <td>${this.escape(t.employees)}</td>
                    <td>${this.escape(t.description)}</td>
                </tr>
            `).join("")
        );
    },

    renderHRHistoriesPage() {
        const items = this.filterItems(this.state.data.hr.histories, ["name", "employee", "position", "department", "description"]);

        return this.renderTablePage(
            "Lịch sử làm việc",
            "Theo dõi lịch sử công việc đã làm của nhân viên",
            "+ Tạo lịch sử",
            "createHistory",
            ["Nhân viên", "Công việc đã làm", "Chức vụ", "Phòng ban", "Bắt đầu", "Kết thúc", "Mô tả"],
            items.map(h => `
                <tr>
                    <td><b>${this.escape(h.employee)}</b></td>
                    <td>${this.escape(h.name)}</td>
                    <td>${this.escape(h.position)}</td>
                    <td>${this.escape(h.department)}</td>
                    <td>${this.escape(h.start)}</td>
                    <td>${this.escape(h.end)}</td>
                    <td>${this.escape(h.description)}</td>
                </tr>
            `).join("")
        );
    },

    renderTablePage(title, subtitle, buttonLabel, buttonAction, headers, rows) {
        return `
            <section class="fit-table-card">
                <div class="fit-table-head">
                    <div>
                        <h2>${this.escape(title)}</h2>
                        <p>${this.escape(subtitle)}</p>
                    </div>
                    <button class="fit-btn primary" data-action="${buttonAction}">${buttonLabel}</button>
                </div>

                <div class="fit-table-wrap">
                    <table class="fit-table">
                        <thead>
                            <tr>${headers.map(h => `<th>${this.escape(h)}</th>`).join("")}</tr>
                        </thead>
                        <tbody>${rows}</tbody>
                    </table>
                </div>
            </section>
        `;
    },

    employeeCard(e) {
        return `
            <article class="fit-project-card">
                <div class="fit-project-top">
                    <div>
                        <h3>${this.escape(e.name)}</h3>
                        <p>${this.escape(e.code)}</p>
                    </div>
                    <span class="fit-person-avatar">${this.escape(e.initial)}</span>
                </div>

                <div class="fit-line">💼 Chức vụ: ${this.escape(e.position || "Chưa có")}</div>
                <div class="fit-line">🏢 Phòng ban: ${this.escape(e.department || "Chưa có")}</div>
                <div class="fit-line">✉️ Email: ${this.escape(e.email || "Chưa có")}</div>
                <div class="fit-line">☎️ SĐT: ${this.escape(e.phone || "Chưa có")}</div>
                <div class="fit-line">👥 Nhóm: ${this.escape(e.team_names || "Chưa có")}</div>
            </article>
        `;
    },

    projectCard(p) {
        return `
            <article class="fit-project-card">
                <div class="fit-project-top">
                    <div>
                        <h3>${this.escape(p.name)}</h3>
                        <p>${this.escape(p.code)}</p>
                    </div>
                    <span class="fit-badge status-${this.escape(p.status)}">${this.escape(p.status_label)}</span>
                </div>

                <div class="fit-line">👤 Phụ trách: ${this.escape(p.responsible || "Chưa có")}</div>
                <div class="fit-line">👥 Nhân viên: ${this.escape(p.employee_count)}</div>
                <div class="fit-line">📅 Bắt đầu: ${this.escape(p.start_date || "Chưa có")}</div>
                <div class="fit-line">🏁 Dự kiến kết thúc: ${this.escape(p.expected_end || "Chưa có")}</div>

                <div class="fit-progress-row">
                    <span>Tiến độ</span>
                    <b>${p.progress}%</b>
                </div>
                <div class="fit-progress">
                    <div style="width:${p.progress}%"></div>
                </div>

                <div class="fit-card-actions">
                    <button data-action="aiGenerateForProject" data-id="${p.id}">✨ AI gợi ý công việc</button>
                    <button data-action="projectInProgress" data-id="${p.id}">Đang chạy</button>
                    <button data-action="projectCompleted" data-id="${p.id}">Hoàn thành</button>
                    <button data-action="projectPaused" data-id="${p.id}">Tạm dừng</button>
                </div>
            </article>
        `;
    },

    column(column) {
        let tasks = column.tasks;

        if (this.state.query) {
            tasks = tasks.filter(task => {
                return `${task.name} ${task.code} ${task.project} ${task.responsible}`.toLowerCase().includes(this.state.query);
            });
        }

        return `
            <section class="fit-column ${this.escape(column.status)}">
                <div class="fit-column-head">
                    <h2>${this.escape(column.label)}</h2>
                    <span>${tasks.length}</span>
                </div>

                ${tasks.map(task => this.taskCard(task)).join("")}

                <button class="fit-btn" style="width:100%" data-action="openTaskModal">+ Thêm công việc thủ công</button>
            </section>
        `;
    },

    taskCard(task) {
        const avatars = task.employees.map(emp => `
            <span title="${this.escape(emp.name)}">${this.escape(emp.initial)}</span>
        `).join("");

        const extra = task.extra_employee_count ? `<em>+${task.extra_employee_count}</em>` : "";

        return `
            <article class="fit-card">
                <h3>${this.escape(task.name)}</h3>
                <div class="fit-card-code">${this.escape(task.code)}</div>

                <div class="fit-line">📁 Dự án: <b>${this.escape(task.project)}</b></div>
                <div class="fit-line">👤 Phụ trách: ${this.escape(task.responsible || "Chưa có")}</div>
                <div class="fit-line">🧩 Giai đoạn: ${this.escape(task.stage || "Chưa có")}</div>

                <div class="fit-badges">
                    <span class="fit-badge priority-${this.escape(task.priority)}">${this.escape(task.priority_label)}</span>
                    <span class="fit-badge status-${this.escape(task.status)}">${this.escape(task.status_label)}</span>
                </div>

                <div class="fit-progress-row">
                    <span>Tiến độ</span>
                    <b>${task.progress}%</b>
                </div>
                <div class="fit-progress"><div style="width:${task.progress}%"></div></div>

                <div class="fit-deadline">📅 Hạn chót: ${this.escape(task.deadline || "Chưa có")}</div>

                <div class="fit-card-actions">
                    <button data-action="taskNotStarted" data-id="${task.id}">Chưa bắt đầu</button>
                    <button data-action="taskInProgress" data-id="${task.id}">Đang làm</button>
                    <button data-action="taskCompleted" data-id="${task.id}">Hoàn thành</button>
                    <button data-action="taskDelayed" data-id="${task.id}">Trì hoãn</button>
                </div>

                <div class="fit-avatars">${avatars}${extra}</div>
            </article>
        `;
    },

    upcoming(task) {
        return `
            <div class="fit-upcoming">
                <b>${this.escape(task.deadline || "Chưa có hạn")}</b>
                <span>${this.escape(task.name)}</span>
                <small>${this.escape(task.project)}</small>
            </div>
        `;
    },

    smallLog(log) {
        return `
            <div class="fit-upcoming">
                <b>${this.escape(log.date)}</b>
                <span>${this.escape(log.task)}</span>
                <small>${this.escape(log.progress)}% — ${this.escape(log.state_label)}</small>
            </div>
        `;
    },

    statCard(color, icon, title, value, sub) {
        return `
            <div class="fit-stat">
                <div class="fit-stat-icon ${color}">${icon}</div>
                <div>
                    <span>${this.escape(title)}</span>
                    <strong>${this.escape(value)}</strong>
                    <small>${this.escape(sub)}</small>
                </div>
            </div>
        `;
    },

    filterItems(items, fields) {
        if (!this.state.query) return items;

        return items.filter(item => {
            return fields.map(field => item[field] || "").join(" ").toLowerCase().includes(this.state.query);
        });
    },

    formatMoney(value) {
        return Number(value || 0).toLocaleString("vi-VN");
    },

    createTaskModal() {
        const data = this.state.data;

        return `
            <div class="fit-modal" id="task-modal">
                <div class="fit-modal-card">
                    <h2>Tạo công việc thủ công</h2>

                    <div class="fit-form-grid">
                        <div class="fit-field">
                            <label>Tên công việc</label>
                            <input id="task-name" placeholder="Ví dụ: Thiết kế giao diện quản lý" />
                        </div>

                        <div class="fit-field">
                            <label>Dự án</label>
                            <select id="task-project" onchange="FitApp.refreshEmployeeOptions()">
                                <option value="">-- Chọn dự án --</option>
                                ${data.projects.map(p => `<option value="${p.id}">${this.escape(p.name)}</option>`).join("")}
                            </select>
                        </div>

                        <div class="fit-field">
                            <label>Người phụ trách</label>
                            <select id="task-responsible">
                                <option value="">-- Chọn nhân viên --</option>
                            </select>
                        </div>

                        <div class="fit-field">
                            <label>Ưu tiên</label>
                            <select id="task-priority">
                                <option value="medium">Trung bình</option>
                                <option value="high">Cao</option>
                                <option value="low">Thấp</option>
                            </select>
                        </div>

                        <div class="fit-field">
                            <label>Hạn chót</label>
                            <input id="task-deadline" type="datetime-local" />
                        </div>

                        <div class="fit-field">
                            <label>Mô tả</label>
                            <textarea id="task-description" placeholder="Mô tả ngắn về công việc..."></textarea>
                        </div>
                    </div>

                    <div class="fit-modal-actions">
                        <button class="fit-btn" data-action="closeModal" data-modal="task-modal">Hủy</button>
                        <button class="fit-btn primary" data-action="createTask">Tạo thủ công</button>
                    </div>
                </div>
            </div>
        `;
    },

    createWorkLogModal() {
        const tasks = this.state.data.work.tasks;

        return `
            <div class="fit-modal" id="work-log-modal">
                <div class="fit-modal-card">
                    <h2>Tạo nhật ký công việc</h2>

                    <div class="fit-form-grid">
                        <div class="fit-field">
                            <label>Công việc</label>
                            <select id="log-task">
                                <option value="">-- Chọn công việc --</option>
                                ${tasks.map(t => `<option value="${t.id}">${this.escape(t.name)} — ${this.escape(t.code)}</option>`).join("")}
                            </select>
                        </div>

                        <div class="fit-field">
                            <label>Mức độ hoàn thành (%)</label>
                            <input id="log-progress" type="number" min="0" max="100" value="0" />
                        </div>

                        <div class="fit-field">
                            <label>Mô tả</label>
                            <textarea id="log-description" placeholder="Nội dung thực hiện..."></textarea>
                        </div>
                    </div>

                    <div class="fit-modal-actions">
                        <button class="fit-btn" data-action="closeModal" data-modal="work-log-modal">Hủy</button>
                        <button class="fit-btn primary" data-action="createWorkLog">Tạo nhật ký</button>
                    </div>
                </div>
            </div>
        `;
    },

    createEvaluationModal() {
        const tasks = this.state.data.work.tasks;
        const employees = this.state.data.employees;

        return `
            <div class="fit-modal" id="evaluation-modal">
                <div class="fit-modal-card">
                    <h2>Tạo đánh giá nhân viên</h2>

                    <div class="fit-form-grid">
                        <div class="fit-field">
                            <label>Nhân viên</label>
                            <select id="eval-employee">
                                <option value="">-- Chọn nhân viên --</option>
                                ${employees.map(e => `<option value="${e.id}">${this.escape(e.name)}</option>`).join("")}
                            </select>
                        </div>

                        <div class="fit-field">
                            <label>Công việc</label>
                            <select id="eval-task">
                                <option value="">-- Không gắn công việc --</option>
                                ${tasks.map(t => `<option value="${t.id}">${this.escape(t.name)} — ${this.escape(t.code)}</option>`).join("")}
                            </select>
                        </div>

                        <div class="fit-field">
                            <label>Điểm số</label>
                            <select id="eval-score">
                                ${Array.from({ length: 10 }, (_, i) => i + 1).map(score => `<option value="${score}">${score}</option>`).join("")}
                            </select>
                        </div>

                        <div class="fit-field">
                            <label>Nhận xét</label>
                            <textarea id="eval-comment" placeholder="Nhận xét về nhân viên..."></textarea>
                        </div>
                    </div>

                    <div class="fit-modal-actions">
                        <button class="fit-btn" data-action="closeModal" data-modal="evaluation-modal">Hủy</button>
                        <button class="fit-btn primary" data-action="createEvaluation">Tạo đánh giá</button>
                    </div>
                </div>
            </div>
        `;
    },

    openModal(id) {
        const modal = document.getElementById(id);
        if (modal) modal.classList.add("show");

        if (id === "task-modal") {
            this.refreshEmployeeOptions();
        }
    },

    closeModal(id) {
        const modal = document.getElementById(id);
        if (modal) modal.classList.remove("show");
    },

    refreshEmployeeOptions() {
        const data = this.state.data;
        const projectId = Number(document.getElementById("task-project")?.value || 0);
        const select = document.getElementById("task-responsible");
        if (!select) return;

        const project = data.projects.find(p => p.id === projectId);
        const allowedIds = project ? project.employee_ids : [];
        const employees = data.employees.filter(emp => allowedIds.includes(emp.id));

        select.innerHTML = `
            <option value="">-- Chọn nhân viên --</option>
            ${employees.map(emp => `<option value="${emp.id}">${this.escape(emp.name)}</option>`).join("")}
        `;
    },

    promptProjectId() {
        const projects = this.state.data.project.projects;
        if (!projects.length) {
            this.toast("Chưa có dự án.");
            return 0;
        }

        const text = projects.map(p => `${p.id}: ${p.name}`).join("\\n");
        return Number(prompt("Chọn ID dự án:\\n" + text) || 0);
    },

    promptBudgetId() {
        const budgets = this.state.data.project.budgets;
        if (!budgets.length) {
            this.toast("Chưa có ngân sách.");
            return 0;
        }

        const text = budgets.map(b => `${b.id}: ${b.name} — ${b.project}`).join("\\n");
        return Number(prompt("Chọn ID ngân sách:\\n" + text) || 0);
    },

    async aiGenerateTasks(projectId = 0) {
        const project_id = projectId || this.promptProjectId();
        if (!project_id) return;

        const note = prompt("Ghi chú thêm cho AI về dự án này, có thể bỏ trống:") || "";

        this.toast("Đang gọi AI Ollama để sinh công việc cho dự án...");

        const result = await this.rpc("/fit/api/ai/generate-tasks", {
            project_id,
            note,
        });

        if (!result.ok) {
            console.log("AI raw:", result.raw || "");
            return this.toast(result.error || "AI sinh công việc thất bại.");
        }

        this.toast(`AI đã tạo ${result.created_count} công việc cho dự án.`);
        await this.load();
        this.setPage("work_tasks");
    },

    async createTask() {
        const result = await this.rpc("/fit/api/task/create", {
            name: document.getElementById("task-name").value,
            project_id: document.getElementById("task-project").value,
            responsible_id: document.getElementById("task-responsible").value,
            priority: document.getElementById("task-priority").value,
            deadline: document.getElementById("task-deadline").value,
            description: document.getElementById("task-description").value,
        });

        if (!result.ok) return this.toast(result.error || "Không tạo được công việc.");

        this.closeModal("task-modal");
        this.toast("Đã tạo công việc.");
        await this.load();
    },

    async updateTaskStatus(taskId, status) {
        const result = await this.rpc("/fit/api/task/status", { task_id: taskId, status });
        if (!result.ok) return this.toast(result.error || "Không cập nhật được trạng thái.");

        this.toast("Đã cập nhật trạng thái.");
        await this.load();
    },

    async createWorkLog() {
        const result = await this.rpc("/fit/api/work-log/create", {
            task_id: document.getElementById("log-task").value,
            progress: document.getElementById("log-progress").value,
            description: document.getElementById("log-description").value,
        });

        if (!result.ok) return this.toast(result.error || "Không tạo được nhật ký.");

        this.closeModal("work-log-modal");
        this.toast("Đã tạo nhật ký.");
        await this.load();
        this.setPage("work_logs");
    },

    async createEvaluation() {
        const result = await this.rpc("/fit/api/evaluation/create", {
            employee_id: document.getElementById("eval-employee").value,
            task_id: document.getElementById("eval-task").value,
            score: document.getElementById("eval-score").value,
            comment: document.getElementById("eval-comment").value,
        });

        if (!result.ok) return this.toast(result.error || "Không tạo được đánh giá.");

        this.closeModal("evaluation-modal");
        this.toast("Đã tạo đánh giá.");
        await this.load();
        this.setPage("work_evaluations");
    },

    async createProjectPrompt() {
        const name = prompt("Tên dự án:");
        if (!name) return;

        const result = await this.rpc("/fit/api/project/create", {
            name,
            code: prompt("Mã dự án, bỏ trống để tự sinh:") || "",
            description: prompt("Mô tả dự án, có thể bỏ trống:") || "",
        });

        if (!result.ok) return this.toast(result.error || "Không tạo được dự án.");

        this.toast("Đã tạo dự án.");
        await this.load();
        this.setPage("project_projects");
    },

    async updateProjectStatus(projectId, status) {
        const result = await this.rpc("/fit/api/project/status", { project_id: projectId, status });

        if (!result.ok) return this.toast(result.error || "Không cập nhật được dự án.");

        this.toast("Đã cập nhật trạng thái dự án.");
        await this.load();
    },

    async createStagePrompt() {
        const project_id = this.promptProjectId();
        if (!project_id) return;

        const name = prompt("Tên giai đoạn:");
        if (!name) return;

        const result = await this.rpc("/fit/api/stage/create", {
            project_id,
            name,
            order: prompt("Thứ tự:", "1") || "1",
            description: prompt("Mô tả, có thể bỏ trống:") || "",
        });

        if (!result.ok) return this.toast(result.error || "Không tạo được giai đoạn.");

        this.toast("Đã tạo giai đoạn.");
        await this.load();
        this.setPage("project_stages");
    },

    async createBudgetPrompt() {
        const project_id = this.promptProjectId();
        if (!project_id) return;

        const name = prompt("Tên ngân sách:");
        if (!name) return;

        const planned = prompt("Ngân sách dự toán:", "0") || "0";

        const result = await this.rpc("/fit/api/budget/create", {
            project_id,
            name,
            code: prompt("Mã ngân sách, bỏ trống để tự sinh:") || "",
            planned,
            allocated: prompt("Ngân sách phân bổ:", planned) || planned,
            reserved: prompt("Ngân sách dự trù:", "0") || "0",
        });

        if (!result.ok) return this.toast(result.error || "Không tạo được ngân sách.");

        this.toast("Đã tạo ngân sách.");
        await this.load();
        this.setPage("project_budgets");
    },

    async createExpensePrompt() {
        const budget_id = this.promptBudgetId();
        if (!budget_id) return;

        const name = prompt("Tên khoản chi:");
        if (!name) return;

        const result = await this.rpc("/fit/api/expense/create", {
            budget_id,
            name,
            amount: prompt("Số tiền:", "0") || "0",
            date: prompt("Ngày chi tiêu YYYY-MM-DD, bỏ trống lấy hôm nay:") || "",
            description: prompt("Mô tả, có thể bỏ trống:") || "",
            over_reason: prompt("Lý do vượt ngân sách nếu có, có thể bỏ trống:") || "",
        });

        if (!result.ok) return this.toast(result.error || "Không tạo được chi phí.");

        this.toast("Đã tạo chi phí.");
        await this.load();
        this.setPage("project_expenses");
    },

    async createResourcePrompt() {
        const project_id = this.promptProjectId();
        if (!project_id) return;

        const name = prompt("Tên tài nguyên:");
        if (!name) return;

        const result = await this.rpc("/fit/api/resource/create", {
            project_id,
            name,
            quantity: prompt("Số lượng:", "1") || "1",
            unit: prompt("Đơn vị:", "cái") || "cái",
            description: prompt("Mô tả, có thể bỏ trống:") || "",
        });

        if (!result.ok) return this.toast(result.error || "Không tạo được tài nguyên.");

        this.toast("Đã tạo tài nguyên.");
        await this.load();
        this.setPage("project_resources");
    },

    async createEmployeePrompt() {
        const first_part = prompt("Họ tên đệm:");
        if (!first_part) return;

        const last_name = prompt("Tên:");
        if (!last_name) return;

        const result = await this.rpc("/fit/api/hr/employee/create", {
            first_part,
            last_name,
            code: prompt("Mã định danh, bỏ trống để tự sinh:") || "",
            email: prompt("Email, có thể bỏ trống:") || "",
            phone: prompt("Số điện thoại, có thể bỏ trống:") || "",
            gender: prompt("Giới tính: nam / nu / khac", "nam") || "",
            position_id: prompt("ID chức vụ, có thể bỏ trống:") || "",
            department_id: prompt("ID phòng ban, có thể bỏ trống:") || "",
        });

        if (!result.ok) return this.toast(result.error || "Không tạo được nhân viên.");

        this.toast("Đã tạo nhân viên.");
        await this.load();
        this.setPage("hr_employees");
    },

    async createPositionPrompt() {
        const name = prompt("Tên chức vụ:");
        if (!name) return;

        const result = await this.rpc("/fit/api/hr/position/create", {
            name,
            code: prompt("Mã chức vụ, bỏ trống để tự sinh:") || "",
            description: prompt("Mô tả, có thể bỏ trống:") || "",
        });

        if (!result.ok) return this.toast(result.error || "Không tạo được chức vụ.");

        this.toast("Đã tạo chức vụ.");
        await this.load();
        this.setPage("hr_positions");
    },

    async createDepartmentPrompt() {
        const name = prompt("Tên phòng ban:");
        if (!name) return;

        const result = await this.rpc("/fit/api/hr/department/create", {
            name,
            code: prompt("Mã phòng ban, bỏ trống để tự sinh:") || "",
            description: prompt("Mô tả, có thể bỏ trống:") || "",
        });

        if (!result.ok) return this.toast(result.error || "Không tạo được phòng ban.");

        this.toast("Đã tạo phòng ban.");
        await this.load();
        this.setPage("hr_departments");
    },

    async createTeamPrompt() {
        const name = prompt("Tên nhóm dự án:");
        if (!name) return;

        const result = await this.rpc("/fit/api/hr/team/create", {
            name,
            description: prompt("Mô tả, có thể bỏ trống:") || "",
        });

        if (!result.ok) return this.toast(result.error || "Không tạo được nhóm.");

        this.toast("Đã tạo nhóm dự án.");
        await this.load();
        this.setPage("hr_teams");
    },

    async createHistoryPrompt() {
        const employees = this.state.data.hr.employees;
        const employeeText = employees.map(e => `${e.id}: ${e.name}`).join("\\n");
        const employee_id = Number(prompt("Chọn ID nhân viên:\\n" + employeeText) || 0);
        if (!employee_id) return;

        const name = prompt("Tên công việc đã làm:");
        if (!name) return;

        const result = await this.rpc("/fit/api/hr/history/create", {
            employee_id,
            name,
            start: prompt("Ngày bắt đầu YYYY-MM-DD, có thể bỏ trống:") || "",
            end: prompt("Ngày kết thúc YYYY-MM-DD, có thể bỏ trống:") || "",
            description: prompt("Mô tả, có thể bỏ trống:") || "",
        });

        if (!result.ok) return this.toast(result.error || "Không tạo được lịch sử.");

        this.toast("Đã tạo lịch sử làm việc.");
        await this.load();
        this.setPage("hr_histories");
    },
};

window.FitApp = FitApp;
document.addEventListener("DOMContentLoaded", () => FitApp.load());

/* =========================================================
   FIT Modal CRUD Patch
   - Click row/card to open detail
   - Edit / Save / Discard / Delete
   - Replace prompt create forms with modal forms
   - Replace AI prompt with modal form
========================================================= */
(function () {
    if (!window.FitApp || FitApp.__modalCrudPatch) return;
    FitApp.__modalCrudPatch = true;

    const oldRender = FitApp.render.bind(FitApp);

    FitApp.render = function () {
        oldRender();
        this.ensureRecordModal();
    };

    FitApp.ensureRecordModal = function () {
        if (document.getElementById("fit-record-modal")) return;

        const modal = document.createElement("div");
        modal.id = "fit-record-modal";
        modal.className = "fit-modal fit-record-modal";
        modal.innerHTML = `
            <div class="fit-modal-card fit-modal-wide">
                <div id="fit-record-modal-body"></div>
            </div>
        `;
        document.body.appendChild(modal);
    };

    FitApp.kindLabels = {
        task: "Công việc",
        work_log: "Nhật ký công việc",
        evaluation: "Đánh giá nhân viên",

        project: "Dự án",
        stage: "Giai đoạn",
        budget: "Ngân sách",
        expense: "Chi phí",
        resource: "Tài nguyên",

        employee: "Nhân viên",
        position: "Chức vụ",
        department: "Phòng ban",
        team: "Nhóm dự án",
        history: "Lịch sử làm việc",
    };

    FitApp.getSelectOptions = function (source) {
        const data = this.state.data;

        if (source === "projects") {
            return (data.project?.projects || data.projects || []).map(p => ({
                value: p.id,
                label: `${p.code || p.id} - ${p.name}`,
            }));
        }

        if (source === "employees") {
            return (data.hr?.employees || data.employees || []).map(e => ({
                value: e.id,
                label: `${e.code || e.id} - ${e.name}`,
            }));
        }

        if (source === "positions") {
            return (data.hr?.positions || []).map(p => ({
                value: p.id,
                label: `${p.code || p.id} - ${p.name}`,
            }));
        }

        if (source === "departments") {
            return (data.hr?.departments || []).map(d => ({
                value: d.id,
                label: `${d.code || d.id} - ${d.name}`,
            }));
        }

        if (source === "budgets") {
            return (data.project?.budgets || []).map(b => ({
                value: b.id,
                label: `${b.code || b.id} - ${b.name} (${b.project || ""})`,
            }));
        }

        if (source === "tasks") {
            return (data.work?.tasks || []).map(t => ({
                value: t.id,
                label: `${t.code || t.id} - ${t.name}`,
            }));
        }

        return [];
    };

    FitApp.getRecordSchemas = function () {
        return {
            employee: [
                { name: "code", label: "Mã định danh", type: "text" },
                { name: "first_part", label: "Họ tên đệm", type: "text", required: true },
                { name: "last_name", label: "Tên", type: "text", required: true },
                { name: "birth", label: "Ngày sinh", type: "date" },
                { name: "gender", label: "Giới tính", type: "select", options: [
                    { value: "", label: "-- Chọn --" },
                    { value: "nam", label: "Nam" },
                    { value: "nu", label: "Nữ" },
                    { value: "khac", label: "Khác" },
                ] },
                { name: "hometown", label: "Quê quán", type: "text" },
                { name: "email", label: "Email", type: "text" },
                { name: "phone", label: "Số điện thoại", type: "text" },
                { name: "position_id", label: "Chức vụ", type: "select", source: "positions" },
                { name: "department_id", label: "Phòng ban", type: "select", source: "departments" },
            ],

            position: [
                { name: "code", label: "Mã chức vụ", type: "text" },
                { name: "name", label: "Tên chức vụ", type: "text", required: true },
                { name: "description", label: "Mô tả", type: "textarea" },
            ],

            department: [
                { name: "code", label: "Mã phòng ban", type: "text" },
                { name: "name", label: "Tên phòng ban", type: "text", required: true },
                { name: "description", label: "Mô tả", type: "textarea" },
            ],

            team: [
                { name: "name", label: "Tên nhóm dự án", type: "text", required: true },
                { name: "description", label: "Mô tả", type: "textarea" },
            ],

            history: [
                { name: "employee_id", label: "Nhân viên", type: "select", source: "employees", required: true },
                { name: "name", label: "Tên công việc đã làm", type: "text", required: true },
                { name: "start", label: "Ngày bắt đầu", type: "date" },
                { name: "end", label: "Ngày kết thúc", type: "date" },
                { name: "description", label: "Mô tả", type: "textarea" },
            ],

            project: [
                { name: "code", label: "Mã dự án", type: "text" },
                { name: "name", label: "Tên dự án", type: "text", required: true },
                { name: "responsible_id", label: "Người phụ trách", type: "select", source: "employees" },
                { name: "status", label: "Trạng thái", type: "select", options: [
                    { value: "chua_bat_dau", label: "Chưa bắt đầu" },
                    { value: "dang_thuc_hien", label: "Đang thực hiện" },
                    { value: "hoan_thanh", label: "Hoàn thành" },
                    { value: "tam_dung", label: "Tạm dừng" },
                    { value: "huy_bo", label: "Hủy bỏ" },
                ] },
                { name: "start_date", label: "Ngày bắt đầu", type: "date" },
                { name: "expected_end", label: "Ngày kết thúc dự kiến", type: "date" },
                { name: "actual_end", label: "Ngày kết thúc thực tế", type: "date" },
                { name: "description", label: "Mô tả", type: "textarea" },
            ],

            stage: [
                { name: "project_id", label: "Dự án", type: "select", source: "projects", required: true },
                { name: "name", label: "Tên giai đoạn", type: "text", required: true },
                { name: "order", label: "Thứ tự", type: "number" },
                { name: "description", label: "Mô tả", type: "textarea" },
            ],

            budget: [
                { name: "code", label: "Mã ngân sách", type: "text" },
                { name: "project_id", label: "Dự án", type: "select", source: "projects", required: true },
                { name: "name", label: "Tên ngân sách", type: "text", required: true },
                { name: "planned", label: "Ngân sách dự toán", type: "number" },
                { name: "allocated", label: "Ngân sách phân bổ", type: "number" },
                { name: "reserved", label: "Ngân sách dự trù", type: "number" },
            ],

            expense: [
                { name: "budget_id", label: "Ngân sách", type: "select", source: "budgets", required: true },
                { name: "name", label: "Tên khoản chi", type: "text", required: true },
                { name: "amount", label: "Số tiền", type: "number" },
                { name: "date", label: "Ngày chi", type: "date" },
                { name: "description", label: "Mô tả", type: "textarea" },
                { name: "over_reason", label: "Lý do vượt ngân sách", type: "textarea" },
            ],

            resource: [
                { name: "project_id", label: "Dự án", type: "select", source: "projects", required: true },
                { name: "name", label: "Tên tài nguyên", type: "text", required: true },
                { name: "quantity", label: "Số lượng", type: "number" },
                { name: "unit", label: "Đơn vị", type: "text" },
                { name: "description", label: "Mô tả", type: "textarea" },
            ],

            task: [
                { name: "code", label: "Mã công việc", type: "text" },
                { name: "name", label: "Tên công việc", type: "text", required: true },
                { name: "project_id", label: "Dự án", type: "select", source: "projects", required: true },
                { name: "responsible_id", label: "Người phụ trách", type: "select", source: "employees" },
                { name: "priority", label: "Mức ưu tiên", type: "select", options: [
                    { value: "low", label: "Thấp" },
                    { value: "medium", label: "Trung bình" },
                    { value: "high", label: "Cao" },
                ] },
                { name: "status", label: "Trạng thái", type: "select", options: [
                    { value: "not_started", label: "Chưa bắt đầu" },
                    { value: "in_progress", label: "Đang thực hiện" },
                    { value: "completed", label: "Hoàn thành" },
                    { value: "delayed", label: "Trì hoãn" },
                    { value: "cancelled", label: "Hủy bỏ" },
                ] },
                { name: "progress", label: "Tiến độ (%)", type: "number" },
                { name: "deadline", label: "Hạn chót", type: "datetime-local" },
                { name: "description", label: "Mô tả", type: "textarea" },
            ],

            work_log: [
                { name: "task_id", label: "Công việc", type: "select", source: "tasks", required: true },
                { name: "progress", label: "Mức độ hoàn thành (%)", type: "number" },
                { name: "description", label: "Mô tả", type: "textarea" },
            ],

            evaluation: [
                { name: "employee_id", label: "Nhân viên", type: "select", source: "employees", required: true },
                { name: "task_id", label: "Công việc", type: "select", source: "tasks" },
                { name: "score", label: "Điểm số", type: "select", options: Array.from({ length: 10 }, (_, i) => ({ value: String(i + 1), label: String(i + 1) })) },
                { name: "comment", label: "Nhận xét", type: "textarea" },
            ],
        };
    };

    FitApp.dateDisplayToISO = function (value) {
        if (!value) return "";
        const text = String(value).trim();

        if (/^\d{4}-\d{2}-\d{2}/.test(text)) return text.slice(0, 10);

        const parts = text.split("/");
        if (parts.length === 3) {
            const [a, b, c] = parts;
            if (c && c.length === 4) {
                return `${c}-${String(b).padStart(2, "0")}-${String(a).padStart(2, "0")}`;
            }
        }

        return text;
    };

    FitApp.datetimeDisplayToInput = function (value) {
        if (!value) return "";
        const text = String(value).trim();
        const [date, time] = text.split(" ");
        const iso = this.dateDisplayToISO(date);
        if (!time) return iso;
        return `${iso}T${time.slice(0, 5)}`;
    };

    FitApp.getRecordList = function (kind) {
        const d = this.state.data;

        const map = {
            task: d.work?.tasks || [],
            work_log: d.work?.logs || [],
            evaluation: d.work?.evaluations || [],

            project: d.project?.projects || [],
            stage: d.project?.stages || [],
            budget: d.project?.budgets || [],
            expense: d.project?.expenses || [],
            resource: d.project?.resources || [],

            employee: d.hr?.employees || [],
            position: d.hr?.positions || [],
            department: d.hr?.departments || [],
            team: d.hr?.teams || [],
            history: d.hr?.histories || [],
        };

        return map[kind] || [];
    };

    FitApp.findLocalRecord = function (kind, id) {
        return this.getRecordList(kind).find(item => Number(item.id) === Number(id)) || {};
    };

    FitApp.renderRecordField = function (field, record, readonly) {
        let value = record[field.name] ?? "";

        if (field.type === "date") value = this.dateDisplayToISO(value);
        if (field.type === "datetime-local") value = this.datetimeDisplayToInput(value);

        const disabled = readonly ? "disabled" : "";
        const required = field.required ? "required" : "";

        if (field.type === "textarea") {
            return `
                <div class="fit-field fit-field-full">
                    <label>${this.escape(field.label)}</label>
                    <textarea data-field="${field.name}" ${disabled} ${required}>${this.escape(value)}</textarea>
                </div>
            `;
        }

        if (field.type === "select") {
            const options = field.options || this.getSelectOptions(field.source);
            const empty = field.required ? "" : `<option value="">-- Không chọn --</option>`;

            return `
                <div class="fit-field">
                    <label>${this.escape(field.label)}</label>
                    <select data-field="${field.name}" ${disabled} ${required}>
                        ${empty}
                        ${options.map(opt => `
                            <option value="${this.escape(opt.value)}" ${String(opt.value) === String(value) ? "selected" : ""}>
                                ${this.escape(opt.label)}
                            </option>
                        `).join("")}
                    </select>
                </div>
            `;
        }

        return `
            <div class="fit-field">
                <label>${this.escape(field.label)}</label>
                <input type="${field.type || "text"}" data-field="${field.name}" value="${this.escape(value)}" ${disabled} ${required}/>
            </div>
        `;
    };

    FitApp.openRecordModal = function (kind, id = 0, mode = "view", defaults = {}) {
        this.ensureRecordModal();

        const record = id ? this.findLocalRecord(kind, id) : defaults;
        const title = id ? `${this.kindLabels[kind]} #${id}` : `Tạo ${this.kindLabels[kind]}`;
        const readonly = mode === "view";
        const schemas = this.getRecordSchemas();
        const fields = schemas[kind] || [];

        this.modalState = { kind, id, mode, original: { ...record } };

        const recordModalEl = document.getElementById("fit-record-modal");
        if (recordModalEl) {
            recordModalEl.dataset.kind = kind;
            recordModalEl.dataset.recordId = String(id || "");
        }

        document.getElementById("fit-record-modal-body").innerHTML = `
            <div class="fit-modal-title-row">
                <h2>${this.escape(title)}</h2>
                <button class="fit-icon-close" onclick="FitApp.closeRecordModal()">×</button>
            </div>

            <div class="fit-form-grid fit-form-grid-two">
                ${fields.map(field => this.renderRecordField(field, record, readonly)).join("")}
            </div>

            <div class="fit-modal-actions">
                ${this.renderRecordModalActions(kind, id, mode)}
            </div>
        `;

        document.getElementById("fit-record-modal").classList.add("show");
    };

    FitApp.renderRecordModalActions = function (kind, id, mode) {
        if (!id) {
            return `
                <button class="fit-btn" onclick="FitApp.closeRecordModal()">Hủy</button>
                <button class="fit-btn primary" onclick="FitApp.saveRecordModal()">Tạo mới</button>
            `;
        }

        if (mode === "view") {
            return `
                <button class="fit-btn danger" onclick="FitApp.deleteRecordModal()">Xóa</button>
                <button class="fit-btn" onclick="FitApp.closeRecordModal()">Đóng</button>
                <button class="fit-btn primary" onclick="FitApp.switchRecordEdit()">Sửa</button>
            `;
        }

        return `
            <button class="fit-btn danger" onclick="FitApp.deleteRecordModal()">Xóa</button>
            <button class="fit-btn" onclick="FitApp.discardRecordEdit()">Hủy</button>
            <button class="fit-btn primary" onclick="FitApp.saveRecordModal()">Lưu</button>
        `;
    };

    FitApp.switchRecordEdit = function () {
        const s = this.modalState;
        this.openRecordModal(s.kind, s.id, "edit", s.original);
    };

    FitApp.discardRecordEdit = function () {
        const s = this.modalState;
        this.openRecordModal(s.kind, s.id, "view", s.original);
    };

    FitApp.closeRecordModal = function () {
        const modal = document.getElementById("fit-record-modal");
        if (modal) modal.classList.remove("show");
    };

    FitApp.collectRecordModalValues = function () {
        const values = {};
        document.querySelectorAll("#fit-record-modal [data-field]").forEach(el => {
            values[el.dataset.field] = el.value;
        });
        return values;
    };

    FitApp.saveRecordModal = async function () {
        const modalEl = document.getElementById("fit-record-modal");
        const s = this.modalState || {};

        const kind = String(s.kind || modalEl?.dataset.kind || "").trim();
        const id = Number(s.id || modalEl?.dataset.recordId || 0);

        if (!kind) {
            return this.toast("Không xác định được loại dữ liệu ở frontend.");
        }

        const values = this.collectRecordModalValues();
        values._kind = kind;

        const route = id ? "/fit/api/record/update" : "/fit/api/record/create";
        const params = id
            ? { kind, record_kind: kind, model_kind: kind, id, values }
            : { kind, record_kind: kind, model_kind: kind, values };

        console.log("FIT save record payload:", params);

        const result = await this.rpc(route, params);

        if (!result.ok) {
            console.log("FIT save record error:", result);
            return this.toast(result.error || "Không lưu được dữ liệu.");
        }

        this.toast(id ? "Đã lưu thay đổi." : "Đã tạo mới.");
        this.closeRecordModal();

        const page = this.state.currentPage;
        const moduleName = this.state.currentModule;

        await this.load();

        this.state.currentPage = page;
        this.state.currentModule = moduleName;

        if (moduleName) {
            this.state.expanded[moduleName] = true;
        }

        this.render();
    };

    FitApp.deleteRecordModal = async function () {
        const modalEl = document.getElementById("fit-record-modal");
        const s = this.modalState || {};

        const kind = String(s.kind || modalEl?.dataset.kind || "").trim();
        const id = Number(s.id || modalEl?.dataset.recordId || 0);

        if (!kind || !id) {
            return this.toast("Không xác định được bản ghi cần xóa.");
        }

        if (!confirm(`Xóa ${this.kindLabels[kind] || kind} này?`)) return;

        const result = await this.rpc("/fit/api/record/delete", {
            kind,
            record_kind: kind,
            model_kind: kind,
            id,
        });

        if (!result.ok) {
            console.log("FIT delete record error:", result);
            return this.toast(result.error || "Không xóa được dữ liệu.");
        }

        this.toast("Đã xóa bản ghi.");
        this.closeRecordModal();

        const page = this.state.currentPage;
        const moduleName = this.state.currentModule;

        await this.load();

        this.state.currentPage = page;
        this.state.currentModule = moduleName;

        if (moduleName) {
            this.state.expanded[moduleName] = true;
        }

        this.render();
    };

    FitApp.openAIProjectModal = function (projectId = 0) {
        this.ensureRecordModal();

        document.getElementById("fit-record-modal-body").innerHTML = `
            <div class="fit-modal-title-row">
                <h2>AI gợi ý công việc cho dự án</h2>
                <button class="fit-icon-close" onclick="FitApp.closeRecordModal()">×</button>
            </div>

            <div class="fit-form-grid">
                <div class="fit-field">
                    <label>Dự án</label>
                    <select id="fit-ai-project">
                        ${this.getSelectOptions("projects").map(opt => `
                            <option value="${this.escape(opt.value)}" ${String(opt.value) === String(projectId) ? "selected" : ""}>
                                ${this.escape(opt.label)}
                            </option>
                        `).join("")}
                    </select>
                </div>

                <div class="fit-field fit-field-full">
                    <label>Ghi chú thêm cho AI</label>
                    <textarea id="fit-ai-note" placeholder="Ví dụ: ưu tiên tạo các công việc phân tích, thiết kế UI, kiểm thử..."></textarea>
                </div>

                <div class="fit-ai-note-box">
                    AI sẽ gọi Ollama local với model qwen2.5:1.5b và tạo công việc thật vào dự án đã chọn.
                </div>
            </div>

            <div class="fit-modal-actions">
                <button class="fit-btn" onclick="FitApp.closeRecordModal()">Hủy</button>
                <button class="fit-btn primary" onclick="FitApp.submitAIProjectModal()">Sinh công việc</button>
            </div>
        `;

        document.getElementById("fit-record-modal").classList.add("show");
    };

    FitApp.submitAIProjectModal = async function () {
        const project_id = Number(document.getElementById("fit-ai-project").value || 0);
        const note = document.getElementById("fit-ai-note").value || "";

        if (!project_id) {
            return this.toast("Vui lòng chọn dự án.");
        }

        this.toast("Đang gọi AI Ollama để sinh công việc...");

        const result = await this.rpc("/fit/api/ai/generate-tasks", {
            project_id,
            note,
        });

        if (!result.ok) {
            console.log("AI raw:", result.raw || "");
            return this.toast(result.error || "AI sinh công việc thất bại.");
        }

        this.toast(`AI đã tạo ${result.created_count} công việc.`);
        this.closeRecordModal();

        await this.load();
        this.state.currentModule = "work";
        this.state.currentPage = "work_tasks";
        this.state.expanded.work = true;
        this.render();
    };

    /* Override prompt-based create actions */
    FitApp.createEmployeePrompt = function () { this.openRecordModal("employee", 0, "edit"); };
    FitApp.createPositionPrompt = function () { this.openRecordModal("position", 0, "edit"); };
    FitApp.createDepartmentPrompt = function () { this.openRecordModal("department", 0, "edit"); };
    FitApp.createTeamPrompt = function () { this.openRecordModal("team", 0, "edit"); };
    FitApp.createHistoryPrompt = function () { this.openRecordModal("history", 0, "edit"); };

    FitApp.createProjectPrompt = function () { this.openRecordModal("project", 0, "edit"); };
    FitApp.createStagePrompt = function () { this.openRecordModal("stage", 0, "edit"); };
    FitApp.createBudgetPrompt = function () { this.openRecordModal("budget", 0, "edit"); };
    FitApp.createExpensePrompt = function () { this.openRecordModal("expense", 0, "edit"); };
    FitApp.createResourcePrompt = function () { this.openRecordModal("resource", 0, "edit"); };

    FitApp.aiGenerateTasks = function (projectId = 0) {
        this.openAIProjectModal(projectId);
    };

    /* Override table renderers: rows become clickable */
    FitApp.renderHREmployeesPage = function () {
        const items = this.filterItems(this.state.data.hr.employees, ["code", "name", "email", "phone", "position", "department", "gender_label"]);

        return this.renderTablePage(
            "Nhân viên",
            "Click vào một nhân viên để xem chi tiết, sửa hoặc xóa",
            "+ Tạo nhân viên",
            "createEmployee",
            ["Mã", "Họ và tên", "Giới tính", "Email", "SĐT", "Chức vụ", "Phòng ban", "Nhóm dự án"],
            items.map(e => `
                <tr data-record-kind="employee" data-record-id="${e.id}">
                    <td>${this.escape(e.code)}</td>
                    <td><b>${this.escape(e.name)}</b></td>
                    <td>${this.escape(e.gender_label)}</td>
                    <td>${this.escape(e.email)}</td>
                    <td>${this.escape(e.phone)}</td>
                    <td>${this.escape(e.position)}</td>
                    <td>${this.escape(e.department)}</td>
                    <td>${this.escape(e.team_names)}</td>
                </tr>
            `).join("")
        );
    };

    FitApp.renderHRPositionsPage = function () {
        const items = this.filterItems(this.state.data.hr.positions, ["code", "name", "description"]);

        return this.renderTablePage(
            "Chức vụ",
            "Click vào một chức vụ để xem chi tiết, sửa hoặc xóa",
            "+ Tạo chức vụ",
            "createPosition",
            ["Mã", "Tên chức vụ", "Số nhân viên", "Mô tả"],
            items.map(p => `
                <tr data-record-kind="position" data-record-id="${p.id}">
                    <td>${this.escape(p.code)}</td>
                    <td><b>${this.escape(p.name)}</b></td>
                    <td>${p.employee_count}</td>
                    <td>${this.escape(p.description)}</td>
                </tr>
            `).join("")
        );
    };

    FitApp.renderHRDepartmentsPage = function () {
        const items = this.filterItems(this.state.data.hr.departments, ["code", "name", "description"]);

        return this.renderTablePage(
            "Phòng ban",
            "Click vào một phòng ban để xem chi tiết, sửa hoặc xóa",
            "+ Tạo phòng ban",
            "createDepartment",
            ["Mã", "Tên phòng ban", "Số nhân viên", "Mô tả"],
            items.map(d => `
                <tr data-record-kind="department" data-record-id="${d.id}">
                    <td>${this.escape(d.code)}</td>
                    <td><b>${this.escape(d.name)}</b></td>
                    <td>${d.employee_count}</td>
                    <td>${this.escape(d.description)}</td>
                </tr>
            `).join("")
        );
    };

    FitApp.renderHRTeamsPage = function () {
        const items = this.filterItems(this.state.data.hr.teams, ["name", "description", "employees"]);

        return this.renderTablePage(
            "Nhóm dự án",
            "Click vào một nhóm để xem chi tiết, sửa hoặc xóa",
            "+ Tạo nhóm",
            "createTeam",
            ["Tên nhóm", "Số thành viên", "Thành viên", "Mô tả"],
            items.map(t => `
                <tr data-record-kind="team" data-record-id="${t.id}">
                    <td><b>${this.escape(t.name)}</b></td>
                    <td>${t.employee_count}</td>
                    <td>${this.escape(t.employees)}</td>
                    <td>${this.escape(t.description)}</td>
                </tr>
            `).join("")
        );
    };

    FitApp.renderHRHistoriesPage = function () {
        const items = this.filterItems(this.state.data.hr.histories, ["name", "employee", "position", "department", "description"]);

        return this.renderTablePage(
            "Lịch sử làm việc",
            "Click vào một lịch sử để xem chi tiết, sửa hoặc xóa",
            "+ Tạo lịch sử",
            "createHistory",
            ["Nhân viên", "Công việc đã làm", "Chức vụ", "Phòng ban", "Bắt đầu", "Kết thúc", "Mô tả"],
            items.map(h => `
                <tr data-record-kind="history" data-record-id="${h.id}">
                    <td><b>${this.escape(h.employee)}</b></td>
                    <td>${this.escape(h.name)}</td>
                    <td>${this.escape(h.position)}</td>
                    <td>${this.escape(h.department)}</td>
                    <td>${this.escape(h.start)}</td>
                    <td>${this.escape(h.end)}</td>
                    <td>${this.escape(h.description)}</td>
                </tr>
            `).join("")
        );
    };

    FitApp.renderProjectProjectsPage = function () {
        const items = this.filterItems(this.state.data.project.projects, ["name", "code", "responsible", "status_label", "employee_names"]);

        return this.renderTablePage(
            "Dự án",
            "Click vào một dự án để xem chi tiết, sửa hoặc xóa",
            "+ Tạo dự án",
            "createProject",
            ["Mã", "Tên dự án", "Phụ trách", "Nhân viên", "Trạng thái", "Tiến độ", "Thao tác"],
            items.map(p => `
                <tr data-record-kind="project" data-record-id="${p.id}">
                    <td>${this.escape(p.code)}</td>
                    <td><b>${this.escape(p.name)}</b></td>
                    <td>${this.escape(p.responsible || "Chưa có")}</td>
                    <td>${this.escape(p.employee_count)}</td>
                    <td><span class="fit-badge status-${this.escape(p.status)}">${this.escape(p.status_label)}</span></td>
                    <td>${p.progress}%</td>
                    <td>
                        <button class="fit-mini-btn" data-action="aiGenerateForProject" data-id="${p.id}">✨ AI</button>
                        <button class="fit-mini-btn" data-action="projectInProgress" data-id="${p.id}">Đang chạy</button>
                        <button class="fit-mini-btn" data-action="projectCompleted" data-id="${p.id}">Hoàn thành</button>
                        <button class="fit-mini-btn" data-action="projectPaused" data-id="${p.id}">Tạm dừng</button>
                    </td>
                </tr>
            `).join("")
        );
    };

    FitApp.renderProjectStagesPage = function () {
        const items = this.filterItems(this.state.data.project.stages, ["name", "project", "description"]);

        return this.renderTablePage(
            "Giai đoạn",
            "Click vào một giai đoạn để xem chi tiết, sửa hoặc xóa",
            "+ Tạo giai đoạn",
            "createStage",
            ["Thứ tự", "Tên giai đoạn", "Dự án", "Mô tả"],
            items.map(s => `
                <tr data-record-kind="stage" data-record-id="${s.id}">
                    <td>${s.order}</td>
                    <td><b>${this.escape(s.name)}</b></td>
                    <td>${this.escape(s.project)}</td>
                    <td>${this.escape(s.description)}</td>
                </tr>
            `).join("")
        );
    };

    FitApp.renderProjectBudgetsPage = function () {
        const items = this.filterItems(this.state.data.project.budgets, ["code", "name", "project"]);

        return this.renderTablePage(
            "Ngân sách",
            "Click vào một ngân sách để xem chi tiết, sửa hoặc xóa",
            "+ Tạo ngân sách",
            "createBudget",
            ["Mã", "Tên ngân sách", "Dự án", "Dự toán", "Phân bổ", "Dự trù", "Đã chi", "Chênh lệch"],
            items.map(b => `
                <tr data-record-kind="budget" data-record-id="${b.id}">
                    <td>${this.escape(b.code)}</td>
                    <td><b>${this.escape(b.name)}</b></td>
                    <td>${this.escape(b.project)}</td>
                    <td>${this.formatMoney(b.planned)}</td>
                    <td>${this.formatMoney(b.allocated)}</td>
                    <td>${this.formatMoney(b.reserved)}</td>
                    <td>${this.formatMoney(b.spent)}</td>
                    <td>${this.formatMoney(b.difference)}</td>
                </tr>
            `).join("")
        );
    };

    FitApp.renderProjectExpensesPage = function () {
        const items = this.filterItems(this.state.data.project.expenses, ["name", "budget", "project", "task", "description"]);

        return this.renderTablePage(
            "Chi phí",
            "Click vào một chi phí để xem chi tiết, sửa hoặc xóa",
            "+ Tạo chi phí",
            "createExpense",
            ["Ngày", "Khoản chi", "Ngân sách", "Dự án", "Công việc", "Số tiền", "Mô tả"],
            items.map(e => `
                <tr data-record-kind="expense" data-record-id="${e.id}">
                    <td>${this.escape(e.date)}</td>
                    <td><b>${this.escape(e.name)}</b></td>
                    <td>${this.escape(e.budget)}</td>
                    <td>${this.escape(e.project)}</td>
                    <td>${this.escape(e.task || "Không gắn")}</td>
                    <td>${this.formatMoney(e.amount)}</td>
                    <td>${this.escape(e.description)}</td>
                </tr>
            `).join("")
        );
    };

    FitApp.renderProjectResourcesPage = function () {
        const items = this.filterItems(this.state.data.project.resources, ["name", "project", "unit", "description"]);

        return this.renderTablePage(
            "Tài nguyên",
            "Click vào một tài nguyên để xem chi tiết, sửa hoặc xóa",
            "+ Tạo tài nguyên",
            "createResource",
            ["Tên tài nguyên", "Dự án", "Số lượng", "Đơn vị", "Mô tả"],
            items.map(r => `
                <tr data-record-kind="resource" data-record-id="${r.id}">
                    <td><b>${this.escape(r.name)}</b></td>
                    <td>${this.escape(r.project)}</td>
                    <td>${this.escape(r.quantity)}</td>
                    <td>${this.escape(r.unit)}</td>
                    <td>${this.escape(r.description)}</td>
                </tr>
            `).join("")
        );
    };

    FitApp.renderWorkTasksPage = function () {
        const tasks = this.filterItems(this.state.data.work.tasks, ["name", "code", "project", "responsible", "status_label", "priority_label"]);

        return this.renderTablePage(
            "Danh sách công việc",
            "Click vào một công việc để xem chi tiết, sửa hoặc xóa",
            "+ Tạo công việc thủ công",
            "openTaskModal",
            ["Mã", "Tên công việc", "Dự án", "Phụ trách", "Ưu tiên", "Trạng thái", "Tiến độ", "Hạn chót", "Thao tác"],
            tasks.map(task => `
                <tr data-record-kind="task" data-record-id="${task.id}">
                    <td>${this.escape(task.code)}</td>
                    <td><b>${this.escape(task.name)}</b></td>
                    <td>${this.escape(task.project)}</td>
                    <td>${this.escape(task.responsible || "Chưa có")}</td>
                    <td><span class="fit-badge priority-${this.escape(task.priority)}">${this.escape(task.priority_label)}</span></td>
                    <td><span class="fit-badge status-${this.escape(task.status)}">${this.escape(task.status_label)}</span></td>
                    <td>${task.progress}%</td>
                    <td>${this.escape(task.deadline || "Chưa có")}</td>
                    <td>
                        <button class="fit-mini-btn" data-action="taskInProgress" data-id="${task.id}">Đang làm</button>
                        <button class="fit-mini-btn" data-action="taskCompleted" data-id="${task.id}">Hoàn thành</button>
                    </td>
                </tr>
            `).join("")
        );
    };

    FitApp.renderWorkLogsPage = function () {
        const logs = this.filterItems(this.state.data.work.logs, ["name", "task", "project", "employees", "state_label", "description"]);

        return this.renderTablePage(
            "Nhật ký công việc",
            "Click vào một nhật ký để xem chi tiết, sửa hoặc xóa",
            "+ Tạo nhật ký",
            "openWorkLogModal",
            ["Ngày", "Công việc", "Dự án", "Người thực hiện", "Mức độ", "Trạng thái", "Mô tả"],
            logs.map(log => `
                <tr data-record-kind="work_log" data-record-id="${log.id}">
                    <td>${this.escape(log.date)}</td>
                    <td><b>${this.escape(log.task)}</b></td>
                    <td>${this.escape(log.project)}</td>
                    <td>${this.escape(log.employees || "Chưa có")}</td>
                    <td>${log.progress}%</td>
                    <td>${this.escape(log.state_label)}</td>
                    <td>${this.escape(log.description)}</td>
                </tr>
            `).join("")
        );
    };

    FitApp.renderEvaluationsPage = function () {
        const items = this.filterItems(this.state.data.work.evaluations, ["employee", "task", "project", "score", "comment"]);

        return this.renderTablePage(
            "Đánh giá nhân viên",
            "Click vào một đánh giá để xem chi tiết, sửa hoặc xóa",
            "+ Tạo đánh giá",
            "openEvaluationModal",
            ["Ngày", "Nhân viên", "Công việc", "Dự án", "Điểm", "Nhận xét"],
            items.map(item => `
                <tr data-record-kind="evaluation" data-record-id="${item.id}">
                    <td>${this.escape(item.date)}</td>
                    <td><b>${this.escape(item.employee)}</b></td>
                    <td>${this.escape(item.task || "Không gắn công việc")}</td>
                    <td>${this.escape(item.project || "Không gắn dự án")}</td>
                    <td><span class="fit-score">${this.escape(item.score)}</span></td>
                    <td>${this.escape(item.comment)}</td>
                </tr>
            `).join("")
        );
    };

    document.addEventListener("click", function (event) {
        const actionButton = event.target.closest("[data-action]");
        if (actionButton) return;

        const row = event.target.closest("[data-record-kind][data-record-id]");
        if (!row || !window.FitApp) return;

        event.preventDefault();
        FitApp.openRecordModal(row.dataset.recordKind, Number(row.dataset.recordId), "view");
    });
})();

/* =========================================================
   AI Preview Before Create Patch
   - Sinh gợi ý AI trước
   - Cho sửa/chọn dòng
   - Chỉ tạo công việc khi bấm "Tạo công việc"
========================================================= */
(function () {
    if (!window.FitApp || FitApp.__aiPreviewPatch) return;
    FitApp.__aiPreviewPatch = true;

    FitApp.openAIProjectModal = function (projectId = 0) {
        this.ensureRecordModal();

        document.getElementById("fit-record-modal-body").innerHTML = `
            <div class="fit-modal-title-row">
                <h2>AI gợi ý công việc cho dự án</h2>
                <button class="fit-icon-close" onclick="FitApp.closeRecordModal()">×</button>
            </div>

            <div class="fit-form-grid">
                <div class="fit-field">
                    <label>Dự án</label>
                    <select id="fit-ai-project">
                        ${this.getSelectOptions("projects").map(opt => `
                            <option value="${this.escape(opt.value)}" ${String(opt.value) === String(projectId) ? "selected" : ""}>
                                ${this.escape(opt.label)}
                            </option>
                        `).join("")}
                    </select>
                </div>

                <div class="fit-field fit-field-full">
                    <label>Ghi chú thêm cho AI</label>
                    <textarea id="fit-ai-note" placeholder="Ví dụ: ưu tiên công việc phân tích yêu cầu, thiết kế giao diện, backend API, kiểm thử..."></textarea>
                </div>

                <div class="fit-ai-note-box">
                    Bước 1: bấm <b>Sinh gợi ý AI</b> để AI đề xuất danh sách công việc. 
                    Bước 2: chỉnh sửa/chọn dòng cần tạo. 
                    Bước 3: bấm <b>Tạo công việc</b> để ghi thật vào Odoo.
                </div>
            </div>

            <div class="fit-ai-preview-area" id="fit-ai-preview-area"></div>

            <div class="fit-modal-actions">
                <button class="fit-btn" onclick="FitApp.closeRecordModal()">Đóng</button>
                <button class="fit-btn" onclick="FitApp.submitAISuggestOnly()">Sinh gợi ý AI</button>
                <button class="fit-btn primary" id="fit-ai-create-btn" onclick="FitApp.createSelectedAISuggestions()" disabled>Tạo công việc</button>
            </div>
        `;

        document.getElementById("fit-record-modal").classList.add("show");
    };

    FitApp.submitAISuggestOnly = async function () {
        const project_id = Number(document.getElementById("fit-ai-project").value || 0);
        const note = document.getElementById("fit-ai-note").value || "";

        if (!project_id) {
            return this.toast("Vui lòng chọn dự án.");
        }

        const area = document.getElementById("fit-ai-preview-area");
        area.innerHTML = `
            <div class="fit-ai-loading">
                Đang gọi AI Ollama để sinh danh sách gợi ý...
            </div>
        `;

        const result = await this.rpc("/fit/api/ai/suggest-tasks", {
            project_id,
            note,
        });

        if (!result.ok) {
            console.log("AI raw:", result.raw || "");
            area.innerHTML = `
                <div class="fit-ai-error">
                    ${this.escape(result.error || "AI sinh gợi ý thất bại.")}
                </div>
            `;
            return;
        }

        this.aiSuggestions = result.suggestions || [];

        if (!this.aiSuggestions.length) {
            area.innerHTML = `
                <div class="fit-ai-error">AI không trả về công việc hợp lệ.</div>
            `;
            return;
        }

        area.innerHTML = this.renderAISuggestionTable(this.aiSuggestions);

        const createBtn = document.getElementById("fit-ai-create-btn");
        if (createBtn) createBtn.disabled = false;

        this.toast(`AI đã gợi ý ${this.aiSuggestions.length} công việc. Chưa tạo vào Odoo.`);
    };

    FitApp.renderAISuggestionTable = function (items) {
        const employees = this.getSelectOptions("employees");

        return `
            <div class="fit-ai-preview-title">
                <h3>Danh sách công việc AI đề xuất</h3>
                <p>Có thể sửa trực tiếp từng dòng trước khi tạo.</p>
            </div>

            <div class="fit-table-wrap fit-ai-table-wrap">
                <table class="fit-table fit-ai-table">
                    <thead>
                        <tr>
                            <th>Chọn</th>
                            <th>Tên công việc</th>
                            <th>Ưu tiên</th>
                            <th>Số ngày</th>
                            <th>Người phụ trách</th>
                            <th>Mô tả</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${items.map((item, index) => `
                            <tr data-ai-row="${index}">
                                <td>
                                    <input type="checkbox" data-ai-field="selected" checked />
                                </td>

                                <td>
                                    <input data-ai-field="title" value="${this.escape(item.title)}" />
                                </td>

                                <td>
                                    <select data-ai-field="priority">
                                        <option value="low" ${item.priority === "low" ? "selected" : ""}>Thấp</option>
                                        <option value="medium" ${item.priority === "medium" ? "selected" : ""}>Trung bình</option>
                                        <option value="high" ${item.priority === "high" ? "selected" : ""}>Cao</option>
                                    </select>
                                </td>

                                <td>
                                    <input type="number" min="1" data-ai-field="estimated_days" value="${this.escape(item.estimated_days || 3)}" />
                                </td>

                                <td>
                                    <select data-ai-field="employee_id">
                                        <option value="">-- Không chọn --</option>
                                        ${employees.map(emp => `
                                            <option value="${this.escape(emp.value)}" ${String(emp.value) === String(item.employee_id || "") ? "selected" : ""}>
                                                ${this.escape(emp.label)}
                                            </option>
                                        `).join("")}
                                    </select>
                                </td>

                                <td>
                                    <textarea data-ai-field="description">${this.escape(item.description || "")}</textarea>
                                </td>
                            </tr>
                        `).join("")}
                    </tbody>
                </table>
            </div>
        `;
    };

    FitApp.collectAISuggestionsFromTable = function () {
        const rows = Array.from(document.querySelectorAll("[data-ai-row]"));

        return rows.map(row => {
            const get = (field) => row.querySelector(`[data-ai-field="${field}"]`);

            return {
                selected: !!get("selected")?.checked,
                title: get("title")?.value || "",
                priority: get("priority")?.value || "medium",
                estimated_days: get("estimated_days")?.value || "3",
                employee_id: get("employee_id")?.value || "",
                description: get("description")?.value || "",
            };
        }).filter(item => item.selected && item.title.trim());
    };

    FitApp.createSelectedAISuggestions = async function () {
        const project_id = Number(document.getElementById("fit-ai-project").value || 0);
        const items = this.collectAISuggestionsFromTable();

        if (!project_id) {
            return this.toast("Vui lòng chọn dự án.");
        }

        if (!items.length) {
            return this.toast("Chưa chọn công việc nào để tạo.");
        }

        const createBtn = document.getElementById("fit-ai-create-btn");
        if (createBtn) {
            createBtn.disabled = true;
            createBtn.textContent = "Đang tạo...";
        }

        const result = await this.rpc("/fit/api/ai/create-suggested-tasks", {
            project_id,
            items,
        });

        if (!result.ok) {
            if (createBtn) {
                createBtn.disabled = false;
                createBtn.textContent = "Tạo công việc";
            }
            return this.toast(result.error || "Không tạo được công việc.");
        }

        this.toast(`Đã tạo ${result.created_count} công việc vào Odoo.`);
        this.closeRecordModal();

        await this.load();

        this.state.currentModule = "work";
        this.state.currentPage = "work_tasks";
        this.state.expanded.work = true;
        this.render();
    };

    FitApp.aiGenerateTasks = function (projectId = 0) {
        this.openAIProjectModal(projectId);
    };
})();
