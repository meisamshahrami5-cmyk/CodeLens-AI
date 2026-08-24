import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox

from app.core.project_analyzer import ProjectAnalyzer
from app.core.analyzer import CodeAnalyzer


class Dashboard(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("CodeLens AI")
        self.geometry("1200x750")
        self.minsize(1000, 650)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.project_path = None
        self.analysis = None
        self.progress = None

        self._build_layout()

    # =========================================================
    # Layout
    # =========================================================

    def _build_layout(self):

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._create_sidebar()
        self._create_main_area()

    # =========================================================
    # Sidebar
    # =========================================================

    def _create_sidebar(self):

        sidebar = ctk.CTkFrame(
            self,
            width=220,
            corner_radius=0,
        )

        sidebar.grid(
            row=0,
            column=0,
            sticky="nsew",
        )

        sidebar.grid_propagate(False)

        logo = ctk.CTkLabel(
            sidebar,
            text="CodeLens AI",
            font=ctk.CTkFont(
                size=25,
                weight="bold",
            ),
        )

        logo.pack(
            padx=20,
            pady=(30, 5),
        )

        subtitle = ctk.CTkLabel(
            sidebar,
            text="Python Code Analyzer",
            font=ctk.CTkFont(size=12),
        )

        subtitle.pack(
            pady=(0, 30),
        )

        self._add_nav_button(
            sidebar,
            "📊  Dashboard",
            self.show_dashboard,
        )

        self._add_nav_button(
            sidebar,
            "⚠  Issues",
            self.show_issues,
        )

        self._add_nav_button(
            sidebar,
            "📁  Files",
            self.show_files,
        )

        self._add_nav_button(
            sidebar,
            "🛡  Security",
            self.show_security,
        )

        self._add_nav_button(
            sidebar,
            "📈  Metrics",
            self.show_metrics,
        )

        separator = ctk.CTkFrame(
            sidebar,
            height=2,
            fg_color="gray30",
        )

        separator.pack(
            fill="x",
            padx=20,
            pady=25,
        )

        self.analyze_button = ctk.CTkButton(
            sidebar,
            text="ANALYZE PROJECT",
            height=42,
            command=self.select_project,
        )

        self.analyze_button.pack(
            fill="x",
            padx=20,
            pady=10,
        )

        self.project_label = ctk.CTkLabel(
            sidebar,
            text="No project selected",
            wraplength=180,
            font=ctk.CTkFont(size=11),
        )

        self.project_label.pack(
            padx=15,
            pady=10,
        )

    def _add_nav_button(
        self,
        parent,
        text,
        command,
    ):

        button = ctk.CTkButton(
            parent,
            text=text,
            anchor="w",
            height=42,
            fg_color="transparent",
            hover_color=("gray80", "gray25"),
            text_color=("gray10", "gray90"),
            command=command,
        )

        button.pack(
            fill="x",
            padx=12,
            pady=3,
        )

    # =========================================================
    # Main
    # =========================================================

    def _create_main_area(self):

        self.main = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color=("gray95", "gray10"),
        )

        self.main.grid(
            row=0,
            column=1,
            sticky="nsew",
        )

        self.main.grid_columnconfigure(
            0,
            weight=1,
        )

        self.main.grid_rowconfigure(
            1,
            weight=1,
        )

        self.header = ctk.CTkFrame(
            self.main,
            height=80,
            corner_radius=0,
        )

        self.header.grid(
            row=0,
            column=0,
            sticky="ew",
        )

        self.page_title = ctk.CTkLabel(
            self.header,
            text="Dashboard",
            font=ctk.CTkFont(
                size=26,
                weight="bold",
            ),
        )

        self.page_title.pack(
            side="left",
            padx=30,
            pady=25,
        )

        self.content = ctk.CTkScrollableFrame(
            self.main,
            fg_color="transparent",
        )

        self.content.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=20,
            pady=10,
        )

    # =========================================================
    # Clear
    # =========================================================

    def _clear_content(self):

        for widget in self.content.winfo_children():
            widget.destroy()

    # =========================================================
    # Dashboard
    # =========================================================

    def show_dashboard(self):

        self.page_title.configure(
            text="Dashboard"
        )

        self._clear_content()

        if not self.analysis:
            self._show_empty_state()
            return

        scores = self.analysis["scores"]
        stats = self.analysis["statistics"]

        cards = [
            ("CODE QUALITY", f"{scores['code_quality']}/100"),
            ("SECURITY", f"{scores['security']}/100"),
            ("OVERALL", f"{scores['overall']}/100"),
            ("GRADE", scores["grade"]),
        ]

        for index, (title, value) in enumerate(cards):

            self._create_score_card(
                index,
                title,
                value,
            )

        self._create_info_card(
            4,
            "PROJECT STATISTICS",
            [
                f"Python Files: {stats['files']}",
                f"Total Lines: {stats['total_lines']}",
                f"Code Lines: {stats['code_lines']}",
                f"Blank Lines: {stats['blank_lines']}",
            ],
        )

        self._create_info_card(
            5,
            "CODE STRUCTURE",
            [
                f"Functions: {len(self.analysis['ast']['functions'])}",
                f"Classes: {len(self.analysis['ast']['classes'])}",
                f"Imports: {self._count_imports()}",
                f"Complexity Items: {len(self.analysis['quality']['complexity'])}",
            ],
        )

        self._create_info_card(
            6,
            "ISSUES",
            [
                f"AST Issues: {len(self.analysis['ast']['issues'])}",
                f"Security Issues: {len(self.analysis['security']['issues'])}",
                f"TODO / FIXME: {len(self._get_todos())}",
            ],
        )

        self._create_info_card(
            7,
            "QUALITY",
            [
                f"Maintainability: {scores['maintainability']}/100",
                f"Complexity: {scores['complexity']}/100",
                f"Issue Score: {scores['issues']}/100",
            ],
        )

    # =========================================================
    # Empty State
    # =========================================================

    def _show_empty_state(self):

        frame = ctk.CTkFrame(
            self.content,
            corner_radius=20,
        )

        frame.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=80,
        )

        title = ctk.CTkLabel(
            frame,
            text="No Project Analyzed",
            font=ctk.CTkFont(
                size=28,
                weight="bold",
            ),
        )

        title.pack(
            pady=(60, 10),
        )

        text = ctk.CTkLabel(
            frame,
            text="Select a Python project to start analyzing your code.",
        )

        text.pack(
            pady=10,
        )

        button = ctk.CTkButton(
            frame,
            text="SELECT PROJECT",
            width=220,
            height=45,
            command=self.select_project,
        )

        button.pack(
            pady=(20, 60),
        )

    # =========================================================
    # Score Card
    # =========================================================

    def _create_score_card(
        self,
        index,
        title,
        value,
    ):

        card = ctk.CTkFrame(
            self.content,
            corner_radius=15,
        )

        card.grid(
            row=0,
            column=index,
            sticky="ew",
            padx=7,
            pady=7,
        )

        label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(
                size=12,
                weight="bold",
            ),
        )

        label.pack(
            pady=(18, 5),
        )

        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(
                size=28,
                weight="bold",
            ),
        )

        value_label.pack(
            pady=(0, 18),
        )

    # =========================================================
    # Info Card
    # =========================================================

    def _create_info_card(
        self,
        index,
        title,
        items,
    ):

        row = 1 + ((index - 4) // 3)
        column = (index - 4) % 3

        card = ctk.CTkFrame(
            self.content,
            corner_radius=15,
        )

        card.grid(
            row=row,
            column=column,
            sticky="nsew",
            padx=7,
            pady=7,
        )

        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(
                size=16,
                weight="bold",
            ),
        )

        title_label.pack(
            anchor="w",
            padx=18,
            pady=(18, 12),
        )

        for item in items:

            label = ctk.CTkLabel(
                card,
                text=item,
                anchor="w",
            )

            label.pack(
                fill="x",
                padx=18,
                pady=4,
            )

    # =========================================================
    # Issues
    # =========================================================

    def show_issues(self):

        self.page_title.configure(
            text="Issues"
        )

        self._clear_content()

        if not self.analysis:
            self._show_empty_state()
            return

        issues = self.analysis["ast"]["issues"]

        if not issues:

            label = ctk.CTkLabel(
                self.content,
                text="✓ No AST issues found",
                font=ctk.CTkFont(
                    size=22,
                    weight="bold",
                ),
            )

            label.pack(
                pady=80,
            )

            return

        for issue in issues:
            self._create_issue_item(issue)

    def _create_issue_item(self, issue):

        frame = ctk.CTkFrame(
            self.content,
            corner_radius=12,
        )

        frame.pack(
            fill="x",
            padx=5,
            pady=5,
        )

        severity = issue.get(
            "severity",
            "Info",
        )

        title = ctk.CTkLabel(
            frame,
            text=f"{severity}  •  {issue['type']}",
            font=ctk.CTkFont(
                size=15,
                weight="bold",
            ),
            anchor="w",
        )

        title.pack(
            fill="x",
            padx=15,
            pady=(12, 4),
        )

        message = ctk.CTkLabel(
            frame,
            text=(
                f"Line {issue['line']} — "
                f"{issue['message']}"
            ),
            anchor="w",
            wraplength=800,
        )

        message.pack(
            fill="x",
            padx=15,
            pady=(0, 12),
        )

    # =========================================================
    # Files
    # =========================================================

    def show_files(self):

        self.page_title.configure(
            text="Python Files"
        )

        self._clear_content()

        if not self.analysis:
            self._show_empty_state()
            return

        for file in self.analysis["files"]:

            frame = ctk.CTkFrame(
                self.content,
                corner_radius=10,
            )

            frame.pack(
                fill="x",
                padx=5,
                pady=4,
            )

            label = ctk.CTkLabel(
                frame,
                text=str(file),
                anchor="w",
            )

            label.pack(
                fill="x",
                padx=15,
                pady=12,
            )

    # =========================================================
    # Security
    # =========================================================

    def show_security(self):

        self.page_title.configure(
            text="Security"
        )

        self._clear_content()

        if not self.analysis:
            self._show_empty_state()
            return

        score = self.analysis["scores"]["security"]

        self._create_score_card(
            0,
            "SECURITY SCORE",
            f"{score}/100",
        )

        issues = self.analysis["security"]["issues"]

        if not issues:

            label = ctk.CTkLabel(
                self.content,
                text="✓ No security issues found",
                font=ctk.CTkFont(
                    size=20,
                    weight="bold",
                ),
            )

            label.grid(
                row=1,
                column=0,
                columnspan=3,
                pady=60,
            )

            return

        for index, issue in enumerate(issues):

            frame = ctk.CTkFrame(
                self.content,
                corner_radius=12,
            )

            frame.grid(
                row=index + 1,
                column=0,
                columnspan=3,
                sticky="ew",
                padx=5,
                pady=5,
            )

            text = (
                f"{issue['severity']} • "
                f"{issue['test_id']} • "
                f"Line {issue['line']}\n"
                f"{issue['message']}"
            )

            label = ctk.CTkLabel(
                frame,
                text=text,
                anchor="w",
                justify="left",
            )

            label.pack(
                fill="x",
                padx=15,
                pady=12,
            )

    # =========================================================
    # Metrics
    # =========================================================

    def show_metrics(self):

        self.page_title.configure(
            text="Metrics"
        )

        self._clear_content()

        if not self.analysis:
            self._show_empty_state()
            return

        scores = self.analysis["scores"]

        metrics = [
            (
                "Maintainability",
                scores["maintainability"],
            ),
            (
                "Complexity",
                scores["complexity"],
            ),
            (
                "Issue Score",
                scores["issues"],
            ),
        ]

        for index, (name, value) in enumerate(metrics):

            frame = ctk.CTkFrame(
                self.content,
                corner_radius=15,
            )

            frame.pack(
                fill="x",
                padx=10,
                pady=10,
            )

            label = ctk.CTkLabel(
                frame,
                text=f"{name}: {value}/100",
                font=ctk.CTkFont(
                    size=16,
                    weight="bold",
                ),
            )

            label.pack(
                anchor="w",
                padx=20,
                pady=(15, 8),
            )

            progress = ctk.CTkProgressBar(
                frame,
                height=15,
            )

            progress.pack(
                fill="x",
                padx=20,
                pady=(0, 15),
            )

            progress.set(
                value / 100
            )

    # =========================================================
    # Helpers
    # =========================================================

    def _count_imports(self):

        total = 0

        for file in self.analysis["files"]:

            result = CodeAnalyzer(
                file
            ).analyze()

            total += len(
                result["imports"]
            )

        return total

    def _get_todos(self):

        todos = []

        for file in self.analysis["files"]:

            result = CodeAnalyzer(
                file
            ).analyze()

            todos.extend(
                result["todos"]
            )

        return todos

    # =========================================================
    # Project Selection
    # =========================================================

    def select_project(self):

        folder = filedialog.askdirectory(
            title="Select Python Project",
        )

        if not folder:
            return

        self.project_path = folder

        self.project_label.configure(
            text=folder,
        )

        self._start_analysis(folder)

    # =========================================================
    # Background Analysis
    # =========================================================

    def _start_analysis(self, folder):

        self.analyze_button.configure(
            text="ANALYZING...",
            state="disabled",
        )

        self.progress = ctk.CTkProgressBar(
            self.main,
            mode="indeterminate",
        )

        self.progress.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=20,
            pady=(0, 10),
        )

        self.progress.start()

        thread = threading.Thread(
            target=self._run_analysis,
            args=(folder,),
            daemon=True,
        )

        thread.start()

    def _run_analysis(self, folder):

        try:

            analyzer = ProjectAnalyzer(
                folder
            )

            result = analyzer.analyze()

            self.after(
                0,
                lambda: self._analysis_finished(
                    result
                ),
            )

        except Exception as error:

            self.after(
                0,
                lambda: self._analysis_failed(
                    error
                ),
            )

    def _analysis_finished(self, result):

        self.analysis = result

        if self.progress:
            self.progress.stop()
            self.progress.destroy()
            self.progress = None

        self.analyze_button.configure(
            text="ANALYZE PROJECT",
            state="normal",
        )

        self.show_dashboard()

    def _analysis_failed(self, error):

        if self.progress:
            self.progress.stop()
            self.progress.destroy()
            self.progress = None

        self.analyze_button.configure(
            text="ANALYZE PROJECT",
            state="normal",
        )

        messagebox.showerror(
            "Analysis Error",
            str(error),
        )


def main():

    app = Dashboard()
    app.mainloop()


if __name__ == "__main__":
    main()