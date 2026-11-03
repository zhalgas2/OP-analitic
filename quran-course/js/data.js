/* Course content.
 *
 * VIDEO: each lesson has a `video` field. Leave it null until a real lesson
 * video exists, then set ONE of:
 *   video: { youtube: "VIDEO_ID" }          // YouTube embed (privacy mode)
 *   video: { src: "media/alippe-1.mp4" }    // self-hosted MP4/WebM
 */
(function () {
  const LETTERS = [
    ['ا', 'Әлиф'], ['ب', 'Бә'], ['ت', 'Тә'], ['ث', 'Сә'],
    ['ج', 'Жим'], ['ح', 'Ха'], ['خ', 'Хо'],
    ['د', 'Дәл'], ['ذ', 'Зәл'], ['ر', 'Ро'], ['ز', 'Зәй'],
    ['س', 'Син'], ['ش', 'Шин'], ['ص', 'Сод'], ['ض', 'Дод'],
    ['ط', 'То'], ['ظ', 'Зо'], ['ع', 'Айн'], ['غ', 'Ғайн'],
    ['ف', 'Фә'], ['ق', 'Қоф'], ['ك', 'Кәф'], ['ل', 'Ләм'],
    ['م', 'Мим'], ['ن', 'Нун'], ['ه', 'Һә'], ['و', 'Уау'], ['ي', 'Йә'],
  ];
  const GROUPS = [[0, 4], [4, 7], [7, 11], [11, 15], [15, 19], [19, 23], [23, 28]];

  function letterQuiz(group) {
    return group.map(([ch, name], i) => {
      const others = LETTERS.filter(l => l[1] !== name);
      const picks = [];
      for (let k = 0; picks.length < 3; k++) {
        const cand = others[(i * 7 + k * 5 + ch.charCodeAt(0)) % others.length][1];
        if (!picks.includes(cand)) picks.push(cand);
      }
      const options = [name, ...picks];
      // deterministic shuffle so answer position varies
      const shift = (ch.charCodeAt(0) + i) % 4;
      const rotated = options.slice(shift).concat(options.slice(0, shift));
      return { q: 'Бұл қай әріп?', arabic: ch, options: rotated, answer: rotated.indexOf(name) };
    });
  }

  const alippeLessons = GROUPS.map(([a, b], i) => {
    const group = LETTERS.slice(a, b);
    return {
      id: 'a' + (i + 1),
      title: group.map(g => g[1]).join(', '),
      subtitle: group.map(g => g[0]).join('  '),
      duration: '8 мин',
      video: null,
      body: `<p>Бұл сабақта ${group.length} әріппен танысасыз. Әр әріпті қарап, атын дауыстап айтыңыз, содан кейін жаттығуды орындаңыз.</p>`,
      letters: group,
      quiz: letterQuiz(group),
    };
  });

  const tajweedLessons = [
    {
      id: 't1', title: 'Тәжуид деген не?', subtitle: 'Кіріспе', duration: '6 мин', video: null,
      body: '<p><b>Тәжуид</b> — Құран әріптерін өз махражынан, өзіне тән сипаттарымен дұрыс айтып оқу ілімі. Сөздің түбірлік мағынасы — «жақсарту, әсемдеу».</p>',
      quiz: [
        { q: '«Тәжуид» сөзінің мағынасы қандай?', options: ['Жақсарту, әсемдеу', 'Жылдам оқу', 'Жаттау', 'Аударма'], answer: 0 },
        { q: 'Тәжуид нені үйретеді?', options: ['Әріпті дұрыс айтуды', 'Жазу әдемілігін', 'Тарихты', 'Грамматиканы'], answer: 0 },
      ],
    },
    {
      id: 't2', title: 'Махраж', subtitle: 'Әріптердің шығу орны', duration: '9 мин', video: null,
      body: '<p>Әріптер шығатын бес негізгі аймақ бар: <b>ауыз-көмей қуысы</b> (әл-жауф), <b>тамақ</b> (әл-халқ), <b>тіл</b>, <b>ерін</b> және <b>мұрын қуысы</b> (әл-хайшум).</p>',
      quiz: [
        { q: 'Негізгі махраж аймақтары нешеу?', options: ['3', '5', '7', '17'], answer: 1 },
        { q: 'Ғұнна (мұрын дыбысы) қай аймақтан шығады?', options: ['Ерін', 'Тамақ', 'Мұрын қуысы', 'Тіл'], answer: 2 },
      ],
    },
    {
      id: 't3', title: 'Нун сәкин мен тәнуин', subtitle: 'Изһар, Идғам, Иқлаб, Ихфа', duration: '12 мин', video: null,
      body: '<p>Нун сәкин (نْ) немесе тәнуиннен кейін келетін әріпке қарай төрт ереже бар: <b>Изһар</b> — анық оқу (тамақ әріптері ء ه ع ح غ خ), <b>Идғам</b> — сіңіру, <b>Иқлаб</b> — ب алдында мимге айналдыру, <b>Ихфа</b> — жасырып оқу (қалған 15 әріп).</p>',
      quiz: [
        { q: 'Иқлаб қай әріптің алдында болады?', arabic: 'ب ؟', options: ['ب', 'م', 'ن', 'ل'], answer: 0 },
        { q: 'Изһар әріптері қай аймақтан шығады?', options: ['Ерін', 'Тамақ', 'Тіл ұшы', 'Мұрын'], answer: 1 },
        { q: 'Ихфа әріптері нешеу?', options: ['6', '4', '15', '1'], answer: 2 },
      ],
    },
    {
      id: 't4', title: 'Идғам', subtitle: 'يرملون', duration: '8 мин', video: null,
      body: '<p>Идғам әріптері — <span class="ar">ي ر م ل و ن</span> («йармалун»). Ғұннамен идғам: <span class="ar">ي ن م و</span>. Ғұннасыз идғам: <span class="ar">ل ر</span>.</p>',
      quiz: [
        { q: 'Ғұннасыз идғам әріптері қайсы?', options: ['ل ر', 'ي ن', 'م و', 'ب ت'], answer: 0, arabicOptions: true },
        { q: 'Идғам әріптері нешеу?', options: ['4', '5', '6', '8'], answer: 2 },
      ],
    },
    {
      id: 't5', title: 'Қалқала', subtitle: 'قطب جد', duration: '7 мин', video: null,
      body: '<p>Қалқала — сәкин әріпті айтқанда пайда болатын жеңіл «серпіліс» дыбысы. Әріптері: <span class="ar">ق ط ب ج د</span> («қутбу жад»).</p>',
      quiz: [
        { q: 'Қайсысы қалқала әрпі?', options: ['س', 'ق', 'م', 'ه'], answer: 1, arabicOptions: true },
        { q: 'Қалқала әріптері нешеу?', options: ['3', '5', '6', '7'], answer: 1 },
      ],
    },
    {
      id: 't6', title: 'Мадд', subtitle: 'Созып оқу', duration: '9 мин', video: null,
      body: '<p>Мадд — дауысты созып оқу. Мадд әріптері: <span class="ar">ا و ي</span>. <b>Мадд табиғи</b> 2 харакат мөлшерінде созылады.</p>',
      quiz: [
        { q: 'Мадд табиғи неше харакат созылады?', options: ['1', '2', '4', '6'], answer: 1 },
        { q: 'Мадд әріптері қайсы?', options: ['ا و ي', 'ق ط ب', 'ل ر ن', 'ء ه ع'], answer: 0, arabicOptions: true },
      ],
    },
  ];

  function opts(correct, candidates) {
    const set = [correct];
    for (const c of candidates) if (c >= 1 && c <= 114 && !set.includes(c) && set.length < 4) set.push(c);
    const shift = correct % 4;
    const list = set.map(String);
    const rotated = list.slice(shift).concat(list.slice(0, shift));
    return { options: rotated, answer: rotated.indexOf(String(correct)) };
  }
  const surah = (id, name, number, ayahs, meaning) => ({
    id, title: name, subtitle: `${number}-сүре · ${ayahs} аят`, duration: '10 мин', video: null,
    body: `<p>${meaning}</p><p class="muted">Сүрені алдымен тыңдап, содан кейін қари соңынан қайталаңыз.</p>`,
    quiz: [
      { q: `«${name}» сүресінде неше аят бар?`, ...opts(ayahs, [ayahs + 1, ayahs - 1, ayahs + 3, ayahs + 2]) },
      { q: `«${name}» Құранның нешінші сүресі?`, ...opts(number, [number - 1, number + 1, number - 5, number + 2, number + 4]) },
    ],
  });

  const quranLessons = [
    surah('q1', 'Әл-Фатиха', 1, 7, '«Ашушы» сүре. Әр намаз рәкағатында оқылады; Алланы мадақтау және тура жол сұрау туралы.'),
    surah('q2', 'Әл-Кәусар', 108, 3, 'Құрандағы ең қысқа сүре. Пайғамбарымызға (с.ғ.с.) берілген Кәусар нығметі, намаз және құрбандық туралы.'),
    surah('q3', 'Әл-Ықылас', 112, 4, 'Алланың бірлігі (тәухид) туралы сүре.'),
    surah('q4', 'Әл-Фәлақ', 113, 5, 'Таң Иесіне сыйынып, жамандықтан пана сұрау туралы.'),
    surah('q5', 'Ән-Нас', 114, 6, 'Адамдардың Раббысына сыйынып, сыбырлаушы шайтаннан пана сұрау туралы.'),
  ];

  window.COURSES = [
    {
      id: 'alippe', title: 'Әліппе', image: 'alippe',
      desc: 'Араб әріптерін танып, дұрыс оқу мен жазуды үйреніңіз',
      lessons: alippeLessons,
    },
    {
      id: 'tajweed', title: 'Тәжуид', image: 'tajweed',
      desc: 'Құранды дұрыс айту мен әуезді оқу ережелері',
      lessons: tajweedLessons,
    },
    {
      id: 'quran', title: 'Құран', image: 'quran',
      desc: 'Сүрелерді тыңдап, оқып, жаттауға арналған сабақтар',
      lessons: quranLessons,
    },
  ];

  window.ACHIEVEMENTS = [
    { id: 'first', title: 'Алғашқы қадам', desc: 'Бірінші сабақты аяқтадыңыз' },
    { id: 'perfect', title: 'Мінсіз нәтиже', desc: 'Жаттығуды 100% орындадыңыз' },
    { id: 'streak3', title: '3 күн қатарынан', desc: 'Үш күн үзбей оқыдыңыз' },
    { id: 'alippe', title: 'Әліппе шебері', desc: 'Әліппе курсын толық аяқтадыңыз' },
    { id: 'tajweed', title: 'Тәжуид білгірі', desc: 'Тәжуид курсын толық аяқтадыңыз' },
    { id: 'quran', title: 'Сүре жаттаушы', desc: 'Құран курсын толық аяқтадыңыз' },
    { id: 'all', title: 'Толық курс', desc: 'Барлық курсты аяқтадыңыз' },
  ];
})();
