/* Persistent user state (localStorage, with in-memory fallback). */
(function () {
  const KEY = 'quranCourse.v1';
  const defaults = () => ({
    name: '',
    completed: {},      // { courseId: { lessonId: { at, score } } }
    achievements: {},   // { id: timestamp }
    streak: { count: 0, last: null },
    settings: { fontScale: 1, reduceMotion: false, dailyGoal: 1 },
  });

  let state;
  try {
    state = Object.assign(defaults(), JSON.parse(localStorage.getItem(KEY) || '{}'));
    state.settings = Object.assign(defaults().settings, state.settings);
  } catch (e) { state = defaults(); }

  function save() {
    try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) { /* private mode */ }
  }

  const today = () => new Date().toISOString().slice(0, 10);

  function touchStreak() {
    const t = today();
    if (state.streak.last === t) return;
    const y = new Date(Date.now() - 864e5).toISOString().slice(0, 10);
    state.streak.count = state.streak.last === y ? state.streak.count + 1 : 1;
    state.streak.last = t;
  }

  function award(id, list) {
    if (!state.achievements[id]) { state.achievements[id] = Date.now(); list.push(id); }
  }

  window.Store = {
    get state() { return state; },
    save,
    isDone(courseId, lessonId) { return !!(state.completed[courseId] || {})[lessonId]; },
    progress(course) {
      const done = course.lessons.filter(l => this.isDone(course.id, l.id)).length;
      return { done, total: course.lessons.length, pct: Math.round(done / course.lessons.length * 100) };
    },
    complete(course, lessonId, score) {
      const newly = [];
      state.completed[course.id] = state.completed[course.id] || {};
      const prev = state.completed[course.id][lessonId];
      state.completed[course.id][lessonId] = { at: Date.now(), score: Math.max(score, prev ? prev.score : 0) };
      touchStreak();
      award('first', newly);
      if (score === 100) award('perfect', newly);
      if (state.streak.count >= 3) award('streak3', newly);
      if (this.progress(course).done === course.lessons.length) award(course.id, newly);
      if (window.COURSES.every(c => this.progress(c).done === c.lessons.length)) award('all', newly);
      save();
      return newly;
    },
    totalDone() {
      return window.COURSES.reduce((n, c) => n + this.progress(c).done, 0);
    },
    currentStreak() {
      const s = state.streak;
      if (!s.last) return 0;
      const y = new Date(Date.now() - 864e5).toISOString().slice(0, 10);
      return s.last === today() || s.last === y ? s.count : 0;
    },
    reset() { state = defaults(); save(); },
  };
})();
