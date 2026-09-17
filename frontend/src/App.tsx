import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
} from "react";
import {
  Link,
  NavLink,
  Route,
  Routes,
  useLocation,
  useNavigate,
  useParams,
} from "react-router-dom";
import {
  ArrowDownToLine,
  ArrowRight,
  ArrowUpRight,
  BarChart3,
  BookOpen,
  Bookmark,
  Check,
  CheckCircle2,
  ChevronRight,
  CircleHelp,
  Clock3,
  Code2,
  Command,
  Database,
  FlaskConical,
  GraduationCap,
  LayoutDashboard,
  Loader2,
  LogOut,
  Menu,
  Moon,
  Play,
  RotateCcw,
  Search,
  Send,
  ShieldCheck,
  Sparkles,
  Sun,
  Target,
  Terminal,
  TrendingUp,
  Trophy,
  X,
  XCircle,
  Zap,
} from "lucide-react";
import CodeEditor from "./CodeEditor";
import Playground from "./Playground";
import { api } from "./api";
import { Checkmark, Code, DataTable, PlotPreview, Tag } from "./components";
import type {
  Catalog,
  Challenge,
  Feedback,
  Grade,
  Progress,
  Question,
  Session,
} from "./types";

interface AcademyState {
  catalog: Catalog;
  progress: Progress;
  session: Session;
  refresh: () => Promise<void>;
  notify: (message: string) => void;
  runner: boolean | null;
}
const Academy = createContext<AcademyState | null>(null);
function useAcademy() {
  const state = useContext(Academy);
  if (!state) throw new Error("Academy unavailable");
  return state;
}

const navigation = [
  { to: "/", label: "Обзор", icon: LayoutDashboard, end: true },
  { to: "/learn", label: "Программа обучения", icon: BookOpen },
  { to: "/practice", label: "Практика", icon: Code2 },
  { to: "/playground", label: "Python Playground", icon: Terminal },
  { to: "/daily", label: "Практика дня", icon: Zap },
  { to: "/mistakes", label: "Работа над ошибками", icon: RotateCcw },
  { to: "/projects", label: "Проекты", icon: FlaskConical },
  { to: "/progress", label: "Мой прогресс", icon: BarChart3 },
];

export default function App() {
  const [catalog, setCatalog] = useState<Catalog | null>(null);
  const [progress, setProgress] = useState<Progress | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [runner, setRunner] = useState<boolean | null>(null);
  const [menu, setMenu] = useState(false);
  const [account, setAccount] = useState(false);
  const [dark, setDark] = useState(
    localStorage.getItem("academy-theme") !== "light",
  );
  const location = useLocation();
  const refresh = useCallback(async () => {
    const [p, s] = await Promise.all([
      api<Progress>("/progress"),
      api<Session>("/session"),
    ]);
    setProgress(p);
    setSession(s);
  }, []);
  useEffect(() => {
    let active = true;
    async function initialize() {
      const s = await api<Session>("/session");
      const [c, p] = await Promise.all([
        api<Catalog>("/catalog"),
        api<Progress>("/progress"),
      ]);
      if (active) {
        setSession(s);
        setCatalog(c);
        setProgress(p);
      }
      api<{ runnerAvailable: boolean }>("/health")
        .then((h) => {
          if (active) setRunner(h.runnerAvailable);
        })
        .catch(() => {
          if (active) setRunner(false);
        });
    }
    initialize().catch((e) => {
      if (active) setError(String(e.message));
    });
    return () => {
      active = false;
    };
  }, []);
  useEffect(() => {
    document.documentElement.dataset.theme = dark ? "dark" : "light";
    localStorage.setItem("academy-theme", dark ? "dark" : "light");
  }, [dark]);
  useEffect(() => {
    setMenu(false);
    window.scrollTo(0, 0);
  }, [location.pathname]);
  useEffect(() => {
    if (notice) {
      const timer = setTimeout(() => setNotice(""), 6000);
      return () => clearTimeout(timer);
    }
  }, [notice]);
  if (error)
    return (
      <div className="loading-screen">
        <Database size={36} />
        <h1>Не удалось подключиться</h1>
        <p>{error}</p>
        <p>Проверьте, что backend запущен на порту 8000.</p>
        <button className="primary" onClick={() => window.location.reload()}>
          Повторить
        </button>
      </div>
    );
  if (!catalog || !progress || !session)
    return (
      <div className="loading-screen">
        <Loader2 className="spin" size={30} />
        <p>Готовим ваше учебное пространство…</p>
      </div>
    );
  const title =
    navigation.find((n) => n.to !== "/" && location.pathname.startsWith(n.to))
      ?.label ||
    (location.pathname.startsWith("/challenge")
      ? "Рабочее пространство"
      : location.pathname.startsWith("/lesson") ||
          location.pathname.startsWith("/quiz")
        ? "Программа обучения"
        : "Обзор");
  return (
    <Academy.Provider
      value={{ catalog, progress, session, refresh, notify: setNotice, runner }}
    >
      <a className="skip-link" href="#main">
        Перейти к содержимому
      </a>
      <aside className={`sidebar ${menu ? "open" : ""}`}>
        <Link to="/" className="brand">
          <span className="brand-mark">
            <Code2 size={24} />
          </span>
          <span>
            PYTHON<span className="brand-sub">DATA ANALYST ACADEMY</span>
          </span>
        </Link>
        <div className="workspace-label">
          ВАШЕ ПРОСТРАНСТВО <span>v{catalog.version}</span>
        </div>
        <nav aria-label="Основная навигация">
          {navigation.map((n) => (
            <NavLink
              key={n.to}
              to={n.to}
              end={n.end}
              className={({ isActive }) =>
                isActive ? "nav-item active" : "nav-item"
              }
            >
              <n.icon size={18} />
              <span>{n.label}</span>
              {n.to === "/mistakes" &&
                progress.mistakes.filter((m) => !m.resolved).length > 0 && (
                  <span className="nav-count">
                    {progress.mistakes.filter((m) => !m.resolved).length}
                  </span>
                )}
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div className="sidebar-note">
            <div className="note-symbol">
              <Terminal size={18} />
            </div>
            <strong>Учитесь на практике</strong>
            <p>
              Настоящий Python.
              <br />
              Новые данные в каждой проверке.
            </p>
            <Link to="/practice">
              Открыть задачи <ArrowUpRight size={15} />
            </Link>
          </div>
          <button className="profile" onClick={() => setAccount(true)}>
            <span className="avatar">
              {session.demo ? "A" : session.email?.[0].toUpperCase()}
            </span>
            <span>
              <strong>
                {session.demo ? "Будущий аналитик" : session.email}
              </strong>
              <small>{session.demo ? "Демо-профиль" : "Личный аккаунт"}</small>
            </span>
            <ChevronRight size={16} />
          </button>
        </div>
      </aside>
      {menu && (
        <button
          className="sidebar-shade"
          aria-label="Закрыть меню"
          onClick={() => setMenu(false)}
        />
      )}
      <div className="app-body">
        <header className="topbar">
          <div className="breadcrumbs">
            <button
              className="icon-button mobile-menu"
              aria-label="Меню"
              onClick={() => setMenu(!menu)}
            >
              <Menu size={20} />
            </button>
            <span>Академия</span>
            <ChevronRight size={13} />
            <strong>{title}</strong>
          </div>
          <div className="topbar-actions">
            <span className="status-dot" />
            <span className="topbar-caption">Учебное пространство</span>
            <button
              className="icon-button"
              aria-label={dark ? "Светлая тема" : "Тёмная тема"}
              onClick={() => setDark(!dark)}
            >
              {dark ? <Sun size={17} /> : <Moon size={17} />}
            </button>
            <Link to="/learn" className="icon-button" aria-label="Найти урок">
              <Search size={17} />
            </Link>
          </div>
        </header>
        <main id="main" tabIndex={-1}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/learn" element={<Roadmap />} />
            <Route path="/lesson/:id" element={<LessonView />} />
            <Route path="/quiz/:id" element={<QuizView />} />
            <Route path="/practice" element={<Practice />} />
            <Route path="/challenge/:id" element={<ChallengeView />} />
            <Route path="/playground" element={<Playground />} />
            <Route path="/daily" element={<Daily />} />
            <Route path="/mistakes" element={<Mistakes />} />
            <Route path="/progress" element={<ProgressView />} />
            <Route path="/projects" element={<Projects />} />
            <Route path="/projects/:id" element={<ProjectView />} />
            <Route path="/exams" element={<Exams />} />
            <Route
              path="*"
              element={
                <div className="empty">
                  <h1>Страница не найдена</h1>
                  <Link to="/">Вернуться в академию</Link>
                </div>
              }
            />
          </Routes>
        </main>
        <footer className="app-footer">
          <span>Python Data Analyst Academy</span>
          <span>Понимать данные. Писать код. Делать выводы.</span>
          <span>v{catalog.version} · Early access</span>
        </footer>
      </div>
      {notice && (
        <div role="status" className="toast">
          {notice}
          <button
            aria-label="Закрыть уведомление"
            onClick={() => setNotice("")}
          >
            <X size={16} />
          </button>
        </div>
      )}
      {account && <Account onClose={() => setAccount(false)} />}
    </Academy.Provider>
  );
}

function PageHeading({
  eyebrow,
  title,
  description,
  children,
}: {
  eyebrow?: string;
  title: string;
  description: string;
  children?: React.ReactNode;
}) {
  return (
    <div className="page-heading">
      <div>
        {eyebrow && <div className="eyebrow">{eyebrow}</div>}
        <h1>{title}</h1>
        <p>{description}</p>
      </div>
      {children}
    </div>
  );
}

function Dashboard() {
  const { catalog, progress, session, refresh, notify } = useAcademy();
  const navigate = useNavigate();
  const [welcome, setWelcome] = useState(
    !localStorage.getItem("academy-onboarded"),
  );
  const next =
    catalog.lessons.find((l) => !progress.completed.lesson.includes(l.id)) ||
    catalog.lessons[0];
  const percent = Math.round(
    (progress.completed.lesson.length / catalog.lessons.length) * 100,
  );
  async function start(placement: string) {
    try {
      await api("/preferences", {
        placement,
        dailyMinutes: session.dailyMinutes,
      });
      localStorage.setItem("academy-onboarded", "1");
      setWelcome(false);
      await refresh();
      navigate(
        placement === "new"
          ? "/lesson/python-start"
          : placement === "test"
            ? "/exams"
            : "/lesson/pandas-intro",
      );
    } catch (e) {
      notify((e as Error).message);
    }
  }
  return (
    <div className="page dashboard">
      <PageHeading
        eyebrow="ВАШ ПУТЬ В АНАЛИТИКУ"
        title={
          progress.questionsAnswered
            ? "С возвращением в академию"
            : "Большой путь начинается с print()"
        }
        description="От первой строки Python до осмысленных решений на данных."
      >
        <span className="date-label">
          <span className="status-dot" /> Ваш темп · {session.dailyMinutes} мин
          в день
        </span>
      </PageHeading>
      <section className="hero">
        <div className="hero-content">
          <span className="hero-kicker">
            <span /> PYTHON FOR DATA ANALYSIS
          </span>
          <h2>
            Не просто знать Python.
            <br />
            <em>Понимать данные.</em>
          </h2>
          <p>
            Короткие уроки, настоящие таблицы и задачи,
            <br className="desktop-only" /> которые проверяют подход, а не
            запомненный ответ.
          </p>
          <Link className="primary" to={`/lesson/${next.id}`}>
            {progress.completed.lesson.length
              ? "Продолжить обучение"
              : "Начать обучение"}
            <ArrowRight size={17} />
          </Link>
          <div className="hero-meta">
            <span>
              <BookOpen size={13} /> {catalog.lessons.length} уроков
            </span>
            <span>
              <Code2 size={13} /> {catalog.challenges.length} задач
            </span>
            <span>
              <ShieldCheck size={13} /> Hidden-data tests
            </span>
          </div>
        </div>
        <div className="hero-art" aria-hidden="true">
          <div className="orbit orbit-one" />
          <div className="orbit orbit-two" />
          <div className="floating-label">
            <span className="status-dot" /> learn. explore. understand.
          </div>
          <div className="mini-window">
            <div className="window-dots">
              <i />
              <i />
              <i />
              <span>your_first_insight.py</span>
            </div>
            <div className="mini-code">
              <span className="line-number">1</span>
              <span>
                <b>import</b> pandas <b>as</b> pd
              </span>
              <span className="line-number">2</span>
              <span />
              <span className="line-number">3</span>
              <span>
                insights = data.<em>groupby</em>(<q>city</q>)
              </span>
              <span className="line-number">4</span>
              <span>
                insights.<em>revenue.sum</em>()
              </span>
            </div>
            <div className="mini-chart">
              <span style={{ height: "30%" }} />
              <span style={{ height: "49%" }} />
              <span style={{ height: "41%" }} />
              <span style={{ height: "69%" }} />
              <span style={{ height: "61%" }} />
              <span style={{ height: "90%" }} />
              <span style={{ height: "78%" }} />
              <span style={{ height: "100%" }} />
            </div>
            <div className="art-caption">
              FROM RAW DATA TO REAL INSIGHTS <ArrowUpRight size={13} />
            </div>
          </div>
          <div className="python-badge">
            <Code2 size={24} />
          </div>
        </div>
      </section>
      <div className="stats-row">
        {[
          {
            icon: BookOpen,
            title: "Уроки пройдены",
            value: progress.completed.lesson.length,
            total: catalog.lessons.length,
            foot: "Понимание начинается с основ",
          },
          {
            icon: Code2,
            title: "Задачи решены",
            value: progress.completed.challenge.length,
            total: catalog.challenges.length,
            foot: "С проверкой на новых данных",
          },
          {
            icon: Target,
            title: "Точность ответов",
            value: `${progress.quizAccuracy}%`,
            foot: `${progress.questionsAnswered} ответов на вопросы`,
          },
          {
            icon: TrendingUp,
            title: "Прогресс курса",
            value: `${percent}%`,
            foot: "Каждый шаг имеет значение",
          },
        ].map((s) => (
          <div className="stat-card" key={s.title}>
            <div>
              <span>{s.title}</span>
              <s.icon size={17} />
            </div>
            <strong>
              {s.value}
              {s.total !== undefined && <small> / {s.total}</small>}
            </strong>
            <p>{s.foot}</p>
          </div>
        ))}
      </div>
      {welcome && (
        <section className="onboarding">
          <div>
            <Sparkles size={19} />
            <div>
              <h3>Начнём с вашего опыта</h3>
              <p>Подберём удобную точку входа. Любой урок всегда открыт.</p>
            </div>
          </div>
          <div className="onboard-options">
            <button onClick={() => start("new")}>
              Я совсем новичок <ArrowRight size={14} />
            </button>
            <button onClick={() => start("basics")}>Знаю основы Python</button>
            <button onClick={() => start("test")}>
              Проверить свой уровень
            </button>
          </div>
        </section>
      )}
      <div className="dashboard-grid">
        <section>
          <div className="section-heading">
            <h2>Ваш следующий шаг</h2>
            <Link to="/learn">
              Вся программа <ArrowRight size={14} />
            </Link>
          </div>
          <Link className="continue-card" to={`/lesson/${next.id}`}>
            <div className="lesson-icon">
              <BookOpen size={26} />
            </div>
            <div>
              <div className="overline">{next.module}</div>
              <h3>{next.title}</h3>
              <p>{next.summary}</p>
              <div className="lesson-meta">
                <span>
                  <Clock3 size={13} /> {next.minutes} мин
                </span>
                <span>{next.topic}</span>
                <span>Теория + практика</span>
              </div>
            </div>
            <span className="round-arrow">
              <ArrowRight size={20} />
            </span>
          </Link>
          <div className="section-heading practice-heading">
            <h2>Пишем код. Исследуем данные.</h2>
            <Link to="/practice">
              Все задачи <ArrowRight size={14} />
            </Link>
          </div>
          <div className="practice-pair">
            {catalog.challenges
              .filter((c) => ["filter-orders", "revenue-city"].includes(c.id))
              .map((c) => (
                <Link
                  to={`/challenge/${c.id}`}
                  className="practice-card"
                  key={c.id}
                >
                  <div className="card-top">
                    <Database size={21} />
                    <Tag green>{c.library}</Tag>
                  </div>
                  <h3>{c.title}</h3>
                  <p>
                    {c.id === "filter-orders"
                      ? "Найдите нужные строки с помощью булевых масок."
                      : "Превратите позиции заказов в отчёт о выручке."}
                  </p>
                  <div className="card-bottom">
                    <span>
                      {progress.completed.challenge.includes(c.id)
                        ? "✓ Решено"
                        : "Начальный уровень"}
                    </span>
                    <ArrowUpRight size={17} />
                  </div>
                </Link>
              ))}
          </div>
        </section>
        <aside className="dashboard-aside">
          <div className="section-heading">
            <h2>Карта навыков</h2>
            <Link to="/progress" aria-label="Вся карта навыков">
              <ArrowUpRight size={17} />
            </Link>
          </div>
          <div className="skill-card">
            <div className="skill-intro">
              <span className="skill-orb">
                <Target size={25} />
              </span>
              <div>
                <strong>Навыки растут с практикой</strong>
                <p>Теория — начало. Код — подтверждение.</p>
              </div>
            </div>
            {progress.skills
              .filter((s) => s.available)
              .slice(0, 6)
              .map((s) => (
                <div className="skill-row" key={s.topic}>
                  <div>
                    <span>{s.topic}</span>
                    <span>{s.score}%</span>
                  </div>
                  <div className="progress-track">
                    <span style={{ width: `${s.score}%` }} />
                  </div>
                </div>
              ))}
            <Link to="/progress" className="text-link">
              Посмотреть прогресс <ArrowRight size={15} />
            </Link>
          </div>
          <div className="daily-callout">
            <span>
              <Zap size={17} /> НЕБОЛЬШОЙ ШАГ КАЖДЫЙ ДЕНЬ
            </span>
            <h3>
              Практика, которая
              <br />
              становится привычкой
            </h3>
            <p>
              Три вопроса, одна задача и один
              <br />
              аналитический вывод.
            </p>
            <Link to="/daily">
              Открыть практику дня <ArrowRight size={15} />
            </Link>
          </div>
        </aside>
      </div>
      <div className="principle">
        <ShieldCheck size={20} />
        <p>
          <strong>
            Ваш код должен работать с данными, которых вы ещё не видели.
          </strong>
          <span>
            Каждое решение проверяется на нескольких альтернативных наборах
            данных.
          </span>
        </p>
        <span className="outline-tag">BUILT FOR UNDERSTANDING</span>
      </div>
    </div>
  );
}

function Roadmap() {
  const { catalog, progress } = useAcademy();
  const [search, setSearch] = useState("");
  const modules = [...new Set(catalog.lessons.map((l) => l.module))];
  return (
    <div className="page">
      <PageHeading
        eyebrow="LEARNING PATH"
        title="От нуля к анализу данных"
        description="Рекомендуемая последовательность. Все уроки открыты — двигайтесь в своём темпе."
      />
      <div className="roadmap-toolbar">
        <div className="search-input">
          <Search size={17} />
          <input
            aria-label="Поиск уроков"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Название урока, библиотека, тема…"
          />
        </div>
        <Tag>
          {catalog.lessons.length} уроков · {catalog.questions.length} вопросов
        </Tag>
      </div>
      <div className="curriculum">
        {modules.map((module, index) => {
          const lessons = catalog.lessons.filter(
            (l) =>
              l.module === module &&
              `${l.title} ${l.topic} ${l.summary}`
                .toLowerCase()
                .includes(search.toLowerCase()),
          );
          return (
            lessons.length > 0 && (
              <section className="module" key={module}>
                <div className="module-rail">
                  <span>{String(index + 1).padStart(2, "0")}</span>
                </div>
                <div className="module-content">
                  <div className="section-heading">
                    <h2>{module.split(" · ")[1]}</h2>
                    <span>
                      {
                        lessons.filter((l) =>
                          progress.completed.lesson.includes(l.id),
                        ).length
                      }{" "}
                      / {lessons.length} пройдено
                    </span>
                  </div>
                  <div className="lesson-list">
                    {lessons.map((l) => (
                      <Link
                        key={l.id}
                        to={`/lesson/${l.id}`}
                        className="lesson-row"
                      >
                        <Checkmark
                          checked={progress.completed.lesson.includes(l.id)}
                        />
                        <div>
                          <h3>{l.title}</h3>
                          <p>{l.summary}</p>
                        </div>
                        <span className="lesson-duration">
                          <Clock3 size={14} />
                          {l.minutes} мин
                        </span>
                        <Tag>{l.topic}</Tag>
                        <ChevronRight size={17} />
                      </Link>
                    ))}
                  </div>
                </div>
              </section>
            )
          );
        })}
      </div>
      {!catalog.lessons.some((l) =>
        `${l.title} ${l.topic} ${l.summary}`
          .toLowerCase()
          .includes(search.toLowerCase()),
      ) && <p className="empty">По этому запросу уроков нет.</p>}
      <div className="info-banner">
        <GraduationCap size={23} />
        <div>
          <strong>Это первая версия академии</strong>
          <p>
            Расширенный курс, все 71 модуль и полноценная Junior-оценка ещё в
            разработке. Доступные материалы и проверки уже работают.
          </p>
        </div>
        <Link to="/exams">
          Проверить знания <ArrowRight size={14} />
        </Link>
      </div>
    </div>
  );
}

function LessonView() {
  const { id } = useParams();
  const { catalog, progress, refresh, notify } = useAcademy();
  const lesson = catalog.lessons.find((l) => l.id === id);
  const navigate = useNavigate();
  if (!lesson) return <NotFound />;
  async function mark() {
    try {
      await api(`/lessons/${id}/complete`, {});
      await refresh();
      navigate(`/quiz/${id}`);
    } catch (e) {
      notify((e as Error).message);
    }
  }
  async function save() {
    try {
      await api(`/lessons/${id}/bookmark`, {});
      await refresh();
    } catch (e) {
      notify((e as Error).message);
    }
  }
  return (
    <div className="page lesson-page">
      <Link className="back-link" to="/learn">
        ← Программа обучения
      </Link>
      <PageHeading
        eyebrow={lesson.module}
        title={lesson.title}
        description={lesson.summary}
      >
        <button
          className={`secondary ${progress.bookmarks.includes(lesson.id) ? "selected" : ""}`}
          onClick={save}
        >
          <Bookmark size={16} />
          {progress.bookmarks.includes(lesson.id) ? "Сохранено" : "Сохранить"}
        </button>
      </PageHeading>
      <div className="lesson-layout">
        <article className="lesson-article">
          <div className="objectives">
            <span className="overline">ПОСЛЕ УРОКА ВЫ СМОЖЕТЕ</span>
            {lesson.objectives.map((o) => (
              <div key={o}>
                <Check size={15} />
                {o}
              </div>
            ))}
          </div>
          {lesson.sections.map((s, i) => (
            <section key={s.title} id={`section-${i}`}>
              <div className="section-number">
                {String(i + 1).padStart(2, "0")}
              </div>
              <h2>{s.title}</h2>
              <p>{s.text}</p>
              {s.code && <Code>{s.code}</Code>}
            </section>
          ))}
          <div className="lesson-finish">
            <div>
              <CheckCircle2 size={25} />
              <h3>Теперь проверим понимание</h3>
              <p>Вопросы с объяснениями помогут закрепить материал.</p>
            </div>
            <button className="primary" onClick={mark}>
              Урок прочитан · к квизу <ArrowRight size={16} />
            </button>
          </div>
        </article>
        <aside className="lesson-toc">
          <span className="overline">В ЭТОМ УРОКЕ</span>
          {lesson.sections.map((s, i) => (
            <a href={`#section-${i}`} key={s.title}>
              <span>{i + 1}</span>
              {s.title}
            </a>
          ))}
          <div className="toc-info">
            <Clock3 size={16} />
            {lesson.minutes} минут · Level {lesson.level}
          </div>
          <div className="toc-practice">
            <Code2 size={22} />
            <h3>Закрепите кодом</h3>
            {lesson.challengeIds.map((cid) => (
              <Link key={cid} to={`/challenge/${cid}`}>
                {catalog.challenges.find((c) => c.id === cid)?.title}
                <ArrowUpRight size={15} />
              </Link>
            ))}
          </div>
        </aside>
      </div>
    </div>
  );
}

function QuestionCard({
  question,
  onNext,
  position,
}: {
  question: Question;
  onNext?: () => void;
  position?: string;
}) {
  const { refresh, notify } = useAcademy();
  const [selected, setSelected] = useState<number | null>(null);
  const [feedback, setFeedback] = useState<Feedback | null>(null);
  const [busy, setBusy] = useState(false);
  async function submit() {
    if (selected === null) return;
    setBusy(true);
    try {
      setFeedback(
        await api<Feedback>(`/questions/${question.id}/answer`, {
          option: selected,
        }),
      );
      await refresh();
    } catch (e) {
      notify((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <div className="quiz-card">
      <div className="quiz-header">
        <Tag>{question.topic}</Tag>
        <span>{position || "Проверка понимания"}</span>
      </div>
      <h2>{question.prompt}</h2>
      <div
        className="answer-options"
        role="radiogroup"
        aria-label="Варианты ответа"
      >
        {question.options.map((option, index) => (
          <button
            role="radio"
            aria-checked={selected === index}
            key={option}
            className={`answer-option ${selected === index ? "selected" : ""} ${feedback && feedback.correctAnswer === option ? "correct-option" : ""}`}
            disabled={!!feedback}
            onClick={() => setSelected(index)}
          >
            <span className="option-letter">
              {String.fromCharCode(65 + index)}
            </span>
            <code>{option}</code>
            <span className="radio-ring">{selected === index && <span />}</span>
          </button>
        ))}
      </div>
      {feedback && (
        <div
          role="status"
          className={`feedback ${feedback.correct ? "success" : "incorrect"}`}
        >
          <h3>
            {feedback.correct ? (
              <CheckCircle2 size={21} />
            ) : (
              <CircleHelp size={21} />
            )}{" "}
            {feedback.correct
              ? "Верно. Давайте закрепим."
              : "Пока не совсем. Разберёмся вместе."}
          </h3>
          <div className="feedback-answer">
            <span>Ваш ответ</span>
            <code>{feedback.yourAnswer}</code>
          </div>
          <p>{feedback.explanation}</p>
          {!feedback.correct && (
            <>
              <div className="feedback-answer">
                <span>Правильный ответ</span>
                <code>{feedback.correctAnswer}</code>
              </div>
              <p>{feedback.correctExplanation}</p>
            </>
          )}
          <Code>{feedback.example}</Code>
          <Link to={`/lesson/${feedback.lessonId}`}>
            Вернуться к объяснению в уроке <ArrowUpRight size={14} />
          </Link>
        </div>
      )}
      <div className="quiz-actions">
        {!feedback ? (
          <button
            className="primary"
            disabled={selected === null || busy}
            onClick={submit}
          >
            {busy ? (
              <Loader2 className="spin" size={17} />
            ) : (
              <Check size={17} />
            )}
            Проверить ответ
          </button>
        ) : (
          <>
            <button
              className="secondary"
              onClick={() => {
                setFeedback(null);
                setSelected(null);
              }}
            >
              <RotateCcw size={15} />
              Попробовать снова
            </button>
            {onNext && (
              <button className="primary" onClick={onNext}>
                Далее <ArrowRight size={16} />
              </button>
            )}
          </>
        )}
      </div>
    </div>
  );
}

function QuizView() {
  const { id } = useParams();
  const { catalog } = useAcademy();
  const [index, setIndex] = useState(0);
  const questions = catalog.questions.filter((q) => q.lessonId === id);
  const lesson = catalog.lessons.find((l) => l.id === id);
  if (!lesson || !questions.length) return <NotFound />;
  return (
    <div className="page quiz-page">
      <Link className="back-link" to={`/lesson/${id}`}>
        ← Вернуться к уроку
      </Link>
      <PageHeading
        eyebrow="ПРОВЕРКА ПОНИМАНИЯ"
        title={lesson.title}
        description="Ошибка — повод разобраться. После каждого ответа вы увидите объяснение."
      />
      <div className="quiz-progress">
        {questions.map((q, i) => (
          <button
            key={q.id}
            aria-label={`Вопрос ${i + 1}`}
            className={i === index ? "current" : ""}
            onClick={() => setIndex(i)}
          >
            {i + 1}
          </button>
        ))}
      </div>
      {index < questions.length ? (
        <QuestionCard
          key={questions[index].id}
          question={questions[index]}
          position={`${index + 1} / ${questions.length}`}
          onNext={() => setIndex(index + 1)}
        />
      ) : (
        <div className="quiz-complete">
          <Trophy size={36} />
          <h2>Вы разобрали все вопросы</h2>
          <p>Следующий шаг — применить знания на новой таблице.</p>
          <div className="button-row">
            <button className="secondary" onClick={() => setIndex(0)}>
              Повторить квиз
            </button>
            <Link
              className="primary"
              to={`/challenge/${lesson.challengeIds[0]}`}
            >
              Перейти к практике <ArrowRight size={16} />
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}

function Practice() {
  const { catalog, progress } = useAcademy();
  const [filter, setFilter] = useState("Все задачи");
  const [search, setSearch] = useState("");
  const filters = [
    "Все задачи",
    ...new Set(catalog.challenges.map((c) => c.library)),
    "Решённые",
  ];
  const items = catalog.challenges.filter(
    (c) =>
      (filter === "Все задачи" ||
        c.library === filter ||
        (filter === "Решённые" &&
          progress.completed.challenge.includes(c.id))) &&
      `${c.title} ${c.description}`
        .toLowerCase()
        .includes(search.toLowerCase()),
  );
  return (
    <div className="page">
      <PageHeading
        eyebrow="LEARN BY DOING"
        title="От знаний к навыкам"
        description="Пишите настоящий код. Проверяйте гипотезы. Находите решения, которые работают с любыми входными данными."
      />
      <div className="practice-toolbar">
        <div className="filter-tabs">
          {filters.map((f) => (
            <button
              className={f === filter ? "active" : ""}
              onClick={() => setFilter(f)}
              key={f}
            >
              {f}
            </button>
          ))}
        </div>
        <div className="search-input">
          <Search size={16} />
          <input
            aria-label="Поиск задач"
            placeholder="Найти задачу…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </div>
      <div className="challenge-grid">
        {items.map((c, i) => (
          <Link to={`/challenge/${c.id}`} className="practice-card" key={c.id}>
            <div className="card-top">
              <span className="task-number">
                {String(i + 1).padStart(2, "0")}
              </span>
              <Tag green>{c.library}</Tag>
            </div>
            <h3>{c.title}</h3>
            <p>{c.description}</p>
            <div className="card-bottom">
              <span>
                {progress.completed.challenge.includes(c.id) ? (
                  <>
                    <Check size={14} /> Решено
                  </>
                ) : (
                  <>
                    <ShieldCheck size={14} /> Альтернативные данные
                  </>
                )}
              </span>
              <ArrowUpRight size={17} />
            </div>
          </Link>
        ))}
      </div>
      {!items.length && <p className="empty">Подходящих задач пока нет.</p>}
    </div>
  );
}

function ChallengeView() {
  const { id } = useParams();
  const { catalog } = useAcademy();
  const challenge = catalog.challenges.find((c) => c.id === id);
  return challenge ? (
    <ChallengeEditor key={challenge.id} challenge={challenge} />
  ) : (
    <NotFound />
  );
}

function ChallengeEditor({ challenge: c }: { challenge: Challenge }) {
  const { refresh, notify, runner, progress } = useAcademy();
  const [code, setCode] = useState(
    localStorage.getItem(`academy-code-${c.id}`) || c.starterCode,
  );
  const [result, setResult] = useState<Grade | null>(null);
  const [busy, setBusy] = useState("");
  const [hint, setHint] = useState(0);
  const [solution, setSolution] = useState("");
  const [tab, setTab] = useState("Условие");
  const [resultTab, setResultTab] = useState("Результат");
  const [error, setError] = useState("");
  const change = (text: string) => {
    setCode(text);
    localStorage.setItem(`academy-code-${c.id}`, text);
  };
  async function run(mode: "run" | "submit") {
    setBusy(mode);
    setError("");
    setResult(null);
    try {
      const response = await api<Grade>(`/challenges/${c.id}/execute`, {
        code,
        mode,
      });
      setResult(response);
      setResultTab("Результат");
      await refresh();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy("");
    }
  }
  async function format() {
    try {
      const r = await api<{ code: string }>("/format", { code });
      change(r.code);
    } catch (e) {
      notify((e as Error).message);
    }
  }
  async function showSolution() {
    try {
      const r = await api<{ solution: string }>(`/challenges/${c.id}/solution`);
      setSolution(r.solution);
    } catch (e) {
      notify((e as Error).message);
    }
  }
  return (
    <div className="page workspace-page">
      <div className="workspace-heading">
        <div>
          <Link className="back-link" to="/practice">
            ← Все задачи
          </Link>
          <h1>{c.title}</h1>
          <div className="button-row">
            <Tag green>{c.library}</Tag>
            <span className="muted">
              {c.difficulty} · {c.timeLimit} сек · {c.memoryLimit} MB
            </span>
            {progress.completed.challenge.includes(c.id) && (
              <Tag green>✓ Решено</Tag>
            )}
          </div>
        </div>
        <Link className="secondary" to={`/lesson/${c.lessonId}`}>
          <BookOpen size={15} />К уроку
        </Link>
      </div>
      <div className="coding-layout">
        <section className="task-panel">
          <div className="panel-tabs">
            {["Условие", "Данные", "Подсказки"].map((t) => (
              <button
                key={t}
                className={tab === t ? "active" : ""}
                onClick={() => setTab(t)}
              >
                {t}
              </button>
            ))}
          </div>
          <div className="task-content">
            {tab === "Условие" && (
              <>
                <div className="overline">ВАША ЗАДАЧА</div>
                <p className="task-description">{c.description}</p>
                <Code>{c.functionSignature}</Code>
                <h3>Контракт результата</h3>
                <p>{c.outputSchema}</p>
                <p>{c.ordering}</p>
                <h3>Входная таблица</h3>
                <div className="data-dictionary">
                  {Object.entries(c.inputSchema).map(([key, value]) => (
                    <div key={key}>
                      <code>{key}</code>
                      <span>{value}</span>
                    </div>
                  ))}
                </div>
                <DataTable
                  frame={{
                    columns: Object.keys(c.inputSchema),
                    data: c.visibleDataset.map((row) =>
                      Object.keys(c.inputSchema).map((k) => row[k]),
                    ),
                  }}
                  title="Видимый dataset"
                />
                <div className="hint-note">
                  <ShieldCheck size={18} />
                  <p>
                    «Запустить» проверяет пример. «Отправить» запускает
                    дополнительные скрытые наборы данных. Только полная проверка
                    засчитывает задачу.
                  </p>
                </div>
              </>
            )}
            {tab === "Данные" && (
              <>
                <h3>Синтетические учебные данные</h3>
                <p>
                  Набор описывает бизнес-ситуацию из условия. Каждая колонка и
                  допустимые значения определены контрактом. Preview сортируется
                  независимо от входа.
                </p>
                <DataTable
                  frame={{
                    columns: Object.keys(c.inputSchema),
                    data: c.visibleDataset.map((row) =>
                      Object.keys(c.inputSchema).map((k) => row[k]),
                    ),
                  }}
                />
                <button
                  className="secondary"
                  onClick={() => {
                    const keys = Object.keys(c.inputSchema);
                    const csv = [
                      keys,
                      ...c.visibleDataset.map((row) => keys.map((k) => row[k])),
                    ]
                      .map((row) =>
                        row
                          .map(
                            (v) => `"${String(v ?? "").replaceAll('"', '""')}"`,
                          )
                          .join(","),
                      )
                      .join("\n");
                    const url = URL.createObjectURL(
                      new Blob([csv], { type: "text/csv;charset=utf-8" }),
                    );
                    const a = document.createElement("a");
                    a.href = url;
                    a.download = `${c.id}.csv`;
                    a.click();
                    URL.revokeObjectURL(url);
                  }}
                >
                  <ArrowDownToLine size={15} />
                  Скачать CSV
                </button>
              </>
            )}
            {tab === "Подсказки" && (
              <>
                <h3>По одному шагу</h3>
                <p>Попробуйте сначала сформулировать подход самостоятельно.</p>
                {c.hints.slice(0, hint).map((h, i) => (
                  <div className="hint-card" key={h}>
                    <span>Подсказка {i + 1}</span>
                    <p>{h}</p>
                  </div>
                ))}
                {hint < c.hints.length && (
                  <button
                    className="secondary"
                    onClick={() => setHint(hint + 1)}
                  >
                    <CircleHelp size={16} />
                    Открыть подсказку {hint + 1}
                  </button>
                )}
                <hr />
                <button className="text-button" onClick={showSolution}>
                  Показать эталонное решение
                </button>
                {solution && (
                  <>
                    <Code>{solution}</Code>
                    <p className="muted">
                      Прочитайте подход, затем попробуйте воспроизвести решение
                      самостоятельно.
                    </p>
                  </>
                )}
              </>
            )}
          </div>
        </section>
        <section className="editor-panel">
          <div className="editor-top">
            <span>
              <Code2 size={15} />
              {c.kind === "sql" ? "solution.sql" : "solution.py"}
            </span>
            <div>
              {c.kind !== "sql" && (
                <button onClick={format} disabled={!!busy}>
                  Форматировать
                </button>
              )}
              <button
                aria-label="Сбросить код"
                title="Восстановить стартовый код"
                disabled={!!busy}
                onClick={() => {
                  change(c.starterCode);
                  setResult(null);
                }}
              >
                <RotateCcw size={14} />
              </button>
            </div>
          </div>
          <CodeEditor
            value={code}
            height="350px"
            sql={c.kind === "sql"}
            onChange={change}
            editable={!busy}
          />
          <div className="editor-actions">
            <span className="editor-language">
              <span className="status-dot" />
              {c.kind === "sql" ? "SQLite" : "Python 3.12"} · isolated
            </span>
            <div>
              <button
                className="secondary"
                disabled={!!busy}
                onClick={() => run("run")}
              >
                {busy === "run" ? (
                  <Loader2 className="spin" size={15} />
                ) : (
                  <Play size={15} />
                )}
                Запустить
              </button>
              <button
                className="primary"
                disabled={!!busy}
                onClick={() => run("submit")}
              >
                {busy === "submit" ? (
                  <Loader2 className="spin" size={15} />
                ) : (
                  <Send size={15} />
                )}
                Отправить
              </button>
            </div>
          </div>
          <div className="results">
            <div className="panel-tabs">
              {["Результат", "Вывод", "Проверки"].map((t) => (
                <button
                  key={t}
                  className={resultTab === t ? "active" : ""}
                  onClick={() => setResultTab(t)}
                >
                  {t}
                  {t === "Проверки" && result && (
                    <span className="mini-count">
                      {result.tests.filter((t) => t.passed).length}/
                      {result.tests.length}
                    </span>
                  )}
                </button>
              ))}
            </div>
            <div className="result-content" aria-live="polite">
              {error && (
                <div className="feedback incorrect">
                  <h3>
                    <XCircle size={18} />
                    Не удалось выполнить
                  </h3>
                  <p>{error}</p>
                </div>
              )}
              {busy && (
                <div className="result-empty">
                  <Loader2 className="spin" size={25} />
                  <strong>
                    {busy === "submit"
                      ? "Проверяем решение на новых данных…"
                      : "Запускаем пример…"}
                  </strong>
                  <p>Каждый набор выполняется в отдельном контейнере.</p>
                </div>
              )}
              {!result && !busy && !error && (
                <div className="result-empty">
                  <Terminal size={28} />
                  <strong>Здесь появится результат вашего кода</strong>
                  <p>
                    Начните с видимого примера, затем проверьте решение на
                    скрытых данных.
                  </p>
                  {runner === false && (
                    <span className="warning-text">
                      Runner недоступен. Проверьте запуск Docker.
                    </span>
                  )}
                </div>
              )}
              {result && (
                <>
                  <div className={`result-summary ${result.status}`}>
                    <span>
                      {result.status === "passed" ? (
                        <CheckCircle2 size={18} />
                      ) : (
                        <CircleHelp size={18} />
                      )}
                      <strong>
                        {result.status === "passed"
                          ? result.submitted
                            ? "Задача решена · прогресс сохранён"
                            : "Пример пройден · отправьте на полную проверку"
                          : "Есть что улучшить"}
                      </strong>
                    </span>
                    <small>{result.duration.toFixed(2)} сек</small>
                  </div>
                  {resultTab === "Результат" && (
                    <>
                      {result.stderr && <Code>{result.stderr}</Code>}
                      {result.output?.type === "dataframe" && (
                        <DataTable
                          frame={{
                            columns: result.output.columns || [],
                            data: result.output.data || [],
                          }}
                          title="Ваш результат"
                        />
                      )}
                      {result.output?.type === "plot" && (
                        <PlotPreview output={result.output} />
                      )}{" "}
                      {result.output &&
                        ["scalar", "array"].includes(result.output.type) && (
                          <Code>
                            {JSON.stringify(result.output.data, null, 2)}
                          </Code>
                        )}
                      {result.status !== "passed" && (
                        <div className="result-feedback">
                          {result.tests
                            .filter((t) => !t.passed)
                            .map((t, i) => (
                              <p key={i}>
                                <XCircle size={15} />
                                {t.feedback}
                              </p>
                            ))}
                        </div>
                      )}
                      {result.expected && !result.visibleTestsPassed && (
                        <DataTable
                          frame={result.expected}
                          title="Ожидаемый результат на примере"
                        />
                      )}
                    </>
                  )}
                  {resultTab === "Вывод" && (
                    <Code>
                      {result.stdout ||
                        "stdout пуст. Используйте print(), чтобы проверить промежуточный результат."}
                    </Code>
                  )}
                  {resultTab === "Проверки" && (
                    <div className="test-list">
                      {result.tests.map((t, i) => (
                        <div key={i}>
                          <span
                            className={t.passed ? "text-green" : "text-amber"}
                          >
                            {t.passed ? (
                              <CheckCircle2 size={17} />
                            ) : (
                              <XCircle size={17} />
                            )}
                          </span>
                          <span>
                            <strong>
                              {t.hidden
                                ? `Скрытый набор ${i}`
                                : "Видимый пример"}
                            </strong>
                            <small>{t.feedback}</small>
                          </span>
                          <Tag>{t.passed ? "PASS" : "FAIL"}</Tag>
                        </div>
                      ))}
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}

function Daily() {
  const { catalog, progress } = useAcademy();
  const day = Math.floor(Date.now() / 86400000);
  const due = progress.mistakes
    .filter((m) => m.kind === "quiz" && m.ready)
    .map((m) => catalog.questions.find((q) => q.id === m.contentId)!)
    .filter(Boolean);
  const daily = [
    ...due,
    ...catalog.questions.slice(day % catalog.questions.length),
    ...catalog.questions,
  ]
    .filter((q, i, all) => all.findIndex((x) => x.id === q.id) === i)
    .slice(0, 3);
  return (
    <div className="page">
      <PageHeading
        eyebrow="DAILY PRACTICE"
        title="Небольшой шаг сегодня"
        description="Три вопроса, одна задача и один вопрос к данным. Ошибки возвращаются по расписанию повторения."
      />
      <div className="daily-grid">
        {daily.map((q, i) => (
          <QuestionCard
            question={q}
            key={`${day}-${q.id}`}
            position={`Вопрос ${i + 1} / 3`}
          />
        ))}
      </div>
      <div className="daily-bottom">
        <div className="panel padded">
          <Code2 size={25} />
          <h2>Одна задача на pandas</h2>
          <p>Универсальная функция для таблицы с любыми городами.</p>
          <Link to="/challenge/revenue-city" className="primary">
            Открыть задачу <ArrowRight size={16} />
          </Link>
        </div>
        <div className="panel padded">
          <TrendingUp size={25} />
          <h2>Один аналитический вывод</h2>
          <p>
            Выручка выросла на 20%, а количество заказов — на 50%. Как изменился
            средний чек?
          </p>
          <details>
            <summary>Проверить рассуждение</summary>
            <p>
              Новый AOV / старый AOV = 1.2 / 1.5 = 0.8. Средний чек снизился на
              20%. Убедитесь, что периоды и определение заказа сопоставимы.
            </p>
          </details>
        </div>
      </div>
    </div>
  );
}

function Mistakes() {
  const { progress, catalog } = useAcademy();
  const [current, setCurrent] = useState<Question | null>(null);
  return (
    <div className="page">
      <PageHeading
        eyebrow="MISTAKES ARE PART OF LEARNING"
        title="Разобраться. Повторить. Запомнить."
        description="Повторения через 1, 3, 7 и 14 дней после верных ответов. Новая ошибка возвращает материал в практику сразу."
      />
      {!progress.mistakes.length ? (
        <div className="empty-state">
          <CheckCircle2 size={38} />
          <h2>Здесь появятся темы для повторения</h2>
          <p>
            Пока нет ошибочных ответов. Решите квиз или практическую задачу —
            история сохранится автоматически.
          </p>
          <Link className="primary" to="/learn">
            Перейти к урокам <ArrowRight size={16} />
          </Link>
        </div>
      ) : (
        <>
          <div className="lesson-list">
            {progress.mistakes.map((m) => (
              <div className="lesson-row" key={m.contentId}>
                <span
                  className={`mistake-icon ${m.resolved ? "resolved" : ""}`}
                >
                  <RotateCcw size={18} />
                </span>
                <div>
                  <h3>
                    {catalog.questions.find((q) => q.id === m.contentId)
                      ?.prompt ||
                      catalog.challenges.find((c) => c.id === m.contentId)
                        ?.title}
                  </h3>
                  <p>
                    {m.topic} · Ошибок: {m.failures} ·{" "}
                    {m.ready
                      ? "Пора повторить"
                      : `Повторение ${new Date(m.due).toLocaleDateString("ru-RU")}`}
                  </p>
                </div>
                {m.kind === "quiz" ? (
                  <button
                    className="secondary"
                    onClick={() =>
                      setCurrent(
                        catalog.questions.find((q) => q.id === m.contentId)!,
                      )
                    }
                  >
                    Повторить
                  </button>
                ) : (
                  <Link className="secondary" to={`/challenge/${m.contentId}`}>
                    Исправить
                  </Link>
                )}
              </div>
            ))}
          </div>
          {current && (
            <div className="review-question">
              <QuestionCard key={current.id} question={current} />
            </div>
          )}
        </>
      )}
    </div>
  );
}

function ProgressView() {
  const { progress, session, refresh, notify } = useAcademy();
  return (
    <div className="page">
      <PageHeading
        eyebrow="YOUR LEARNING, MEASURED"
        title="Прогресс, подтверждённый практикой"
        description="30% за последние ответы по теме, 70% за задачи, прошедшие все скрытые проверки. Уроки учитываются отдельно."
      />
      <div className="progress-overview">
        <div className="panel padded">
          <Target size={25} />
          <h2>Ваш учебный ритм</h2>
          <p>Сколько времени вы хотите выделять в день?</p>
          <div className="filter-tabs">
            {[30, 60, 90].map((n) => (
              <button
                key={n}
                className={session.dailyMinutes === n ? "active" : ""}
                onClick={async () => {
                  try {
                    await api("/preferences", {
                      placement: session.placement,
                      dailyMinutes: n,
                    });
                    await refresh();
                  } catch (e) {
                    notify((e as Error).message);
                  }
                }}
              >
                {n} мин
              </button>
            ))}
          </div>
          <p className="muted">
            Это ориентир для привычки, а не обещание даты трудоустройства.
          </p>
        </div>
        <div className="panel padded">
          <BarChart3 size={25} />
          <h2>За последние 7 дней</h2>
          <div className="weekly-stats">
            <div>
              <strong>{progress.weekly.lessons}</strong>
              <span>уроков</span>
            </div>
            <div>
              <strong>{progress.weekly.attempts}</strong>
              <span>попыток</span>
            </div>
            <div>
              <strong>{progress.weekly.passed}</strong>
              <span>успешных</span>
            </div>
          </div>
        </div>
      </div>
      <div className="section-heading">
        <h2>Карта навыков</h2>
        <Tag>Теория + код</Tag>
      </div>
      <div className="skills-grid">
        {progress.skills.map((s) => (
          <div
            className={`panel skill-detail ${!s.available ? "unavailable" : ""}`}
            key={s.topic}
          >
            <div>
              <h3>{s.topic}</h3>
              <span>{s.available ? `${s.score}%` : "В планах"}</span>
            </div>
            <div className="progress-track">
              <span style={{ width: `${s.score}%` }} />
            </div>
            <p>
              {s.available
                ? `${s.theoryCount} вопросов · ${s.challengeCount} задач`
                : "Учебный контент ещё не добавлен"}
            </p>
          </div>
        ))}
      </div>
      <div className="section-heading">
        <h2>Последние попытки</h2>
      </div>
      <div className="lesson-list">
        {progress.recentAttempts.map((a) => (
          <div className="lesson-row" key={a.id}>
            {a.correct ? (
              <CheckCircle2 size={18} className="text-green" />
            ) : (
              <CircleHelp size={18} className="text-amber" />
            )}
            <div>
              <h3>{a.contentId}</h3>
              <p>
                {a.kind === "quiz" ? "Вопрос" : "Задача"} ·{" "}
                {new Date(a.createdAt).toLocaleString("ru-RU")}
              </p>
            </div>
            <Tag>{a.correct ? "Пройдено" : "На повторение"}</Tag>
          </div>
        ))}
        {!progress.recentAttempts.length && (
          <p className="empty">История появится после первой попытки.</p>
        )}
      </div>
      <div className="info-banner">
        <GraduationCap size={25} />
        <p>
          Статус Junior не выдаётся за теорию. В этой версии нет
          профессиональной сертификации; итоговая оценка требует практического
          анализа неизвестных данных.
        </p>
      </div>
    </div>
  );
}

function Projects() {
  const { catalog } = useAcademy();
  return (
    <div className="page">
      <PageHeading
        eyebrow="BUILD YOUR ANALYTICAL THINKING"
        title="От задачи к исследованию"
        description="Бизнес-контекст, воспроизводимые данные и критерии самостоятельной проверки. Учитесь объяснять результаты."
      />
      <div className="project-grid">
        {catalog.projects.map((p, i) => (
          <Link className="project-card" to={`/projects/${p.id}`} key={p.id}>
            <div className={`project-cover cover-${i}`}>
              <span>PROJECT / 0{i + 1}</span>
              <BarChart3 size={70} strokeWidth={1} />
              <span>{i === 3 ? "FINAL PROJECT" : "GUIDED ANALYSIS"}</span>
            </div>
            <div className="padded">
              <h2>{p.title}</h2>
              <p>{p.description}</p>
              <div className="card-bottom">
                <span>
                  {p.files.length} CSV · {p.tasks.length} этапов
                </span>
                <ArrowUpRight size={19} />
              </div>
            </div>
          </Link>
        ))}
      </div>
      {!catalog.projects.length && (
        <div className="empty-state">
          <FlaskConical size={30} />
          <h2>Проекты готовятся</h2>
          <p>Сейчас доступны рабочие задачи на фильтрацию и агрегирование.</p>
          <Link to="/practice">Открыть практику</Link>
        </div>
      )}
    </div>
  );
}

function ProjectView() {
  const { id } = useParams();
  const { catalog } = useAcademy();
  const project = catalog.projects.find((p) => p.id === id);
  const [checked, setChecked] = useState<string[]>(() =>
    JSON.parse(localStorage.getItem(`academy-project-${id}`) || "[]"),
  );
  if (!project) return <NotFound />;
  return (
    <div className="page">
      <Link className="back-link" to="/projects">
        ← Все проекты
      </Link>
      <PageHeading
        eyebrow="АНАЛИТИЧЕСКИЙ ПРОЕКТ"
        title={project.title}
        description={project.description}
      />
      <div className="lesson-layout">
        <article className="panel padded">
          <h2>План исследования</h2>
          {project.tasks.map((task, i) => (
            <div className="project-step" key={task}>
              <span>{i + 1}</span>
              <p>{task}</p>
            </div>
          ))}
          <h2>Критерии самостоятельной проверки</h2>
          <p className="muted">
            Чеклист сохраняется в этом браузере. Он не выдаёт оценку и не
            подтверждает уровень Junior.
          </p>
          {project.rubric.map((r) => (
            <label className="rubric-item" key={r}>
              <input
                type="checkbox"
                checked={checked.includes(r)}
                onChange={() => {
                  const next = checked.includes(r)
                    ? checked.filter((x) => x !== r)
                    : [...checked, r];
                  setChecked(next);
                  localStorage.setItem(
                    `academy-project-${id}`,
                    JSON.stringify(next),
                  );
                }}
              />
              {r}
            </label>
          ))}
        </article>
        <aside>
          <div className="panel padded">
            <Database size={24} />
            <h3>Исходные данные</h3>
            <p>
              Синтетические данные, seed 2026. CSV в UTF-8. Описание колонок
              включено в архив.
            </p>
            <a className="primary" href={`/api/projects/${id}/dataset`}>
              <ArrowDownToLine size={16} />
              Скачать ZIP
            </a>
          </div>
          <div className="panel padded project-practice">
            <h3>Связанная практика</h3>
            {project.challengeIds.map((cid) => (
              <Link
                className="project-task-link"
                key={cid}
                to={`/challenge/${cid}`}
              >
                {catalog.challenges.find((c) => c.id === cid)?.title}
                <ArrowRight size={15} />
              </Link>
            ))}
          </div>
        </aside>
      </div>
    </div>
  );
}

function Exams() {
  const { catalog, progress } = useAcademy();
  const [exam, setExam] = useState("placement");
  const [index, setIndex] = useState(0);
  const selected = catalog.exams.find((e) => e.id === exam);
  const questions = selected
    ? selected.questionIds
        .map((id) => catalog.questions.find((q) => q.id === id)!)
        .filter(Boolean)
    : catalog.questions.filter((_, i) => i % 2 === 0).slice(0, 15);
  const tasks = selected?.challengeIds || ["conversion", "filter-orders"];
  const answered = questions.filter((q) =>
    progress.completed.question.includes(q.id),
  ).length;
  return (
    <div className="page">
      <PageHeading
        eyebrow="ASSESSMENT"
        title="Проверьте точку старта"
        description="Учебная проверка знаний и две практические задачи. Результат помогает выбрать следующий урок, но не является сертификацией."
      />
      <div className="filter-tabs exam-tabs">
        <button
          className={exam === "placement" ? "active" : ""}
          onClick={() => {
            setExam("placement");
            setIndex(0);
          }}
        >
          Входная проверка
        </button>
        {catalog.exams.map((e) => (
          <button
            key={e.id}
            className={exam === e.id ? "active" : ""}
            onClick={() => {
              setExam(e.id);
              setIndex(0);
            }}
          >
            {e.title}
          </button>
        ))}
      </div>
      <div className="info-banner">
        <Target size={22} />
        <p>
          По выбранным вопросам правильный ответ хотя бы раз получен: {answered}{" "}
          / {questions.length}. Практика:{" "}
          {
            tasks.filter((id) => progress.completed.challenge.includes(id))
              .length
          }{" "}
          / {tasks.length}. Это накопительный учебный прогресс, а не балл
          независимого экзамена.
        </p>
      </div>
      {questions[index] && (
        <QuestionCard
          key={`${exam}-${questions[index].id}`}
          question={questions[index]}
          position={`${index + 1} / ${questions.length}`}
          onNext={() => setIndex(index + 1)}
        />
      )}{" "}
      {index >= questions.length && (
        <div className="panel padded">
          <h2>Следующий шаг — код</h2>
          <p>
            {answered / questions.length >= 0.8
              ? "Базовая теория знакома. Подтвердите понимание практикой."
              : "Начните с уроков Python и разбора ошибок, затем повторите проверку."}
          </p>
          {tasks.map((id) => (
            <Link
              className="project-task-link"
              key={id}
              to={`/challenge/${id}`}
            >
              {catalog.challenges.find((c) => c.id === id)?.title}
              <ArrowRight size={17} />
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

function Account({ onClose }: { onClose: () => void }) {
  const dialog = useRef<HTMLDivElement>(null);
  const { session, refresh, notify } = useAcademy();
  const [mode, setMode] = useState("register");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  useEffect(() => {
    const previous = document.activeElement as HTMLElement | null;
    dialog.current?.querySelector<HTMLElement>("input, button")?.focus();
    function key(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
      if (e.key === "Tab") {
        const items = Array.from(
          dialog.current?.querySelectorAll<HTMLElement>(
            "button:not(:disabled), input:not(:disabled), a[href]",
          ) || [],
        );
        const first = items[0],
          last = items[items.length - 1];
        if (e.shiftKey && document.activeElement === first) {
          e.preventDefault();
          last?.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault();
          first?.focus();
        }
      }
    }
    document.addEventListener("keydown", key);
    return () => {
      document.removeEventListener("keydown", key);
      previous?.focus();
    };
  }, [onClose]);
  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    try {
      await api(`/auth/${mode}`, { email, password });
      await refresh();
      notify(
        mode === "register"
          ? "Аккаунт создан. Ваш демо-прогресс сохранён."
          : "Вы вошли в аккаунт.",
      );
      onClose();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div
        className="modal"
        ref={dialog}
        role="dialog"
        aria-modal="true"
        aria-labelledby="account-title"
        onClick={(e) => e.stopPropagation()}
      >
        <button
          className="modal-close icon-button"
          aria-label="Закрыть"
          onClick={onClose}
        >
          <X size={20} />
        </button>
        <span className="brand-mark">
          <GraduationCap size={28} />
        </span>
        <h2 id="account-title">
          {session.demo ? "Ваше место в академии" : "Ваш аккаунт"}
        </h2>
        {session.demo ? (
          <>
            <p>
              Создайте аккаунт, чтобы вернуться к прогрессу с другого
              устройства. Демо доступно без регистрации.
            </p>
            <div className="filter-tabs">
              <button
                className={mode === "register" ? "active" : ""}
                onClick={() => setMode("register")}
              >
                Регистрация
              </button>
              <button
                className={mode === "login" ? "active" : ""}
                onClick={() => setMode("login")}
              >
                Вход
              </button>
            </div>
            <form onSubmit={submit}>
              <label>
                Email
                <input
                  autoFocus
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  autoComplete="email"
                />
              </label>
              <label>
                Пароль · минимум 12 символов
                <input
                  type="password"
                  minLength={12}
                  maxLength={128}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  autoComplete={
                    mode === "login" ? "current-password" : "new-password"
                  }
                />
              </label>
              {error && (
                <p className="text-amber" role="alert">
                  {error}
                </p>
              )}
              <button className="primary" disabled={busy}>
                {busy && <Loader2 className="spin" size={16} />}{" "}
                {mode === "register" ? "Создать аккаунт" : "Войти"}{" "}
                <ArrowRight size={16} />
              </button>
            </form>
          </>
        ) : (
          <>
            <p>{session.email}</p>
            <button
              className="secondary"
              onClick={async () => {
                try {
                  await api("/auth/logout", {});
                  window.location.href = "/";
                } catch (e) {
                  notify((e as Error).message);
                }
              }}
            >
              <LogOut size={16} />
              Выйти из аккаунта
            </button>
          </>
        )}
      </div>
    </div>
  );
}

function NotFound() {
  return (
    <div className="empty-state">
      <Command size={30} />
      <h1>Материал не найден</h1>
      <Link to="/learn">Перейти к программе</Link>
    </div>
  );
}
