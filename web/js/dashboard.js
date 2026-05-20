var todayStr = new Date().toISOString().split('T')[0];

var tasks = [
  { name: 'Write project report',         sub: 'Summarize research findings',   priority: 'High',   time: '2h 00m', due: '2024-01-25', status: 'inprogress' },
  { name: 'Complete online course module', sub: 'Chapter 4 — Data Structures',  priority: 'High',   time: '1h 30m', due: '2024-01-25', status: 'inreview'   },
  { name: 'Morning workout session',       sub: 'Cardio + strength training',    priority: 'Medium', time: '45m',    due: todayStr,     status: 'todo'       },
  { name: 'Read 30 pages of book',         sub: 'Atomic Habits — Chapter 6',    priority: 'Low',    time: '40m',    due: todayStr,     status: 'done'       },
];

function escapeHtml(text) {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function formatDate(dateStr) {
  if (!dateStr) return '—';
  var d = new Date(dateStr + 'T00:00:00');
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

function renderTasks(filter) {
  var tbody = document.getElementById('task-tbody');
  tbody.innerHTML = '';

  var filtered = [];
  for (var i = 0; i < tasks.length; i++) {
    var t = tasks[i];
    if (filter === 'high'  && t.priority !== 'High') continue;
    if (filter === 'today' && t.due !== todayStr)    continue;
    if (filter === 'done'  && t.status !== 'done')   continue;
    filtered.push(t);
  }

  for (var i = 0; i < filtered.length; i++) {
    var t = filtered[i];

    var prioClass   = t.priority === 'High' ? 'high' : t.priority === 'Medium' ? 'medium' : 'low';
    var statusClass = t.status;

    var statusLabel = 'To-do';
    if (t.status === 'inprogress') statusLabel = 'In Progress';
    if (t.status === 'inreview')   statusLabel = 'In Review';
    if (t.status === 'done')       statusLabel = 'Done';

    var row = document.createElement('tr');
    row.innerHTML =
      '<td>' +
        '<div class="task-name">' + escapeHtml(t.name) + '</div>' +
        '<div class="task-sub">'  + escapeHtml(t.sub)  + '</div>' +
      '</td>' +
      '<td><span class="pill ' + prioClass + '">' + t.priority + '</span></td>' +
      '<td><span class="time-badge">⏱ ' + escapeHtml(t.time) + '</span></td>' +
      '<td>' + formatDate(t.due) + '</td>' +
      '<td><span class="status-pill ' + statusClass + '">' + statusLabel + '</span></td>';

    tbody.appendChild(row);
  }
}

function updateStats() {
  var total          = tasks.length;
  var doneCount      = 0;
  var dueTodayCount  = 0;
  var trackedMinutes = 0;

  for (var i = 0; i < tasks.length; i++) {
    var t = tasks[i];

    if (t.status === 'done') {
      doneCount++;
      var hours = t.time.match(/(\d+)h/);
      var mins  = t.time.match(/(\d+)m/);
      if (hours) trackedMinutes += parseInt(hours[1]) * 60;
      if (mins)  trackedMinutes += parseInt(mins[1]);
    }

    if (t.due === todayStr && t.status !== 'done') {
      dueTodayCount++;
    }
  }

  var completedPercent = total > 0 ? Math.round(doneCount / total * 100) : 0;

  var trackedStr;
  if (trackedMinutes >= 60) {
    trackedStr = Math.floor(trackedMinutes / 60) + 'h';
    if (trackedMinutes % 60 > 0) trackedStr += ' ' + (trackedMinutes % 60) + 'm';
  } else {
    trackedStr = trackedMinutes + 'm';
  }

  document.getElementById('stat-total').textContent         = total;
  document.getElementById('stat-completed-pct').textContent = completedPercent + '%';
  document.getElementById('stat-bar').style.width           = completedPercent + '%';
  document.getElementById('stat-due-today').textContent     = String(dueTodayCount).padStart(2, '0');
  document.getElementById('stat-tracked').textContent       = trackedStr;
}

function filterTasks(filter, clickedTab) {
  var allTabs = document.querySelectorAll('.tab');
  for (var i = 0; i < allTabs.length; i++) {
    allTabs[i].classList.remove('active');
  }
  clickedTab.classList.add('active');
  renderTasks(filter);
}

function openModal() {
  document.getElementById('task-modal').classList.add('open');
}

function closeModal() {
  document.getElementById('task-modal').classList.remove('open');
  document.getElementById('task-name-input').value = '';
  document.getElementById('task-time').value        = '';
  document.getElementById('task-due').value         = '';
  document.getElementById('task-notes').value       = '';
}

document.getElementById('task-modal').addEventListener('click', function(event) {
  if (event.target === this) {
    closeModal();
  }
});

function saveTask() {
  var name = document.getElementById('task-name-input').value.trim();

  if (name === '') {
    document.getElementById('task-name-input').style.borderColor = '#E8536A';
    setTimeout(function() {
      document.getElementById('task-name-input').style.borderColor = '';
    }, 1500);
    return;
  }

  var category = document.getElementById('task-category').value;
  var priority = document.getElementById('task-priority').value;
  var time     = document.getElementById('task-time').value || '—';
  var due      = document.getElementById('task-due').value  || '';

  if (localStorage.getItem('userHasAddedTask') === null) {
    tasks = [];
    localStorage.setItem('userHasAddedTask', 'yes');
  }

  tasks.push({
    name:     name,
    sub:      category,
    priority: priority,
    time:     time,
    due:      due,
    status:   'todo'
  });

  localStorage.setItem('tasks', JSON.stringify(tasks));

  closeModal();
  renderTasks('all');
  updateStats();

  var successMsg = document.getElementById('success-msg');
  successMsg.style.opacity = 1;
  successMsg.classList.add('show');
  setTimeout(function() {
    successMsg.style.opacity = 0;
    successMsg.classList.remove('show');
  }, 2000);

  var allTabs = document.querySelectorAll('.tab');
  for (var i = 0; i < allTabs.length; i++) {
    allTabs[i].classList.remove('active');
  }
  allTabs[0].classList.add('active');
}

var sectionNames = {
  tasks:   'Task Overview',
  timer:   'Focus Timer',
  journal: 'Daily Journal',
  health:  'Health Hub'
};

function showSection(name, clickedItem) {
  var sections = document.querySelectorAll('.section');
  for (var i = 0; i < sections.length; i++) {
    sections[i].classList.remove('active');
  }

  var items = document.querySelectorAll('.sidebar-item');
  for (var i = 0; i < items.length; i++) {
    items[i].classList.remove('active');
  }

  document.getElementById('section-' + name).classList.add('active');
  if (clickedItem) clickedItem.classList.add('active');

  document.getElementById('topbar-title').textContent = sectionNames[name] || 'Dashboard';
}

function setGreeting() {
  var hour = new Date().getHours();
  var greeting;

  if (hour < 12) {
    greeting = 'Good Morning';
  } else if (hour < 17) {
    greeting = 'Good Afternoon';
  } else {
    greeting = 'Good Evening';
  }

  document.getElementById('app-greeting').textContent = greeting + ', Surya! 👋';
}

setGreeting();

var timerInterval     = null;
var timerSeconds      = 25 * 60;
var timerTotal        = 25 * 60;
var timerRunning      = false;
var isStopwatch       = false;
var stopwatchSecs     = 0;
var timerExtraMinutes = 0;

function setTimerMode(totalSeconds, label, clickedBtn) {
  clearInterval(timerInterval);
  timerRunning = false;

  isStopwatch   = (totalSeconds === 0);
  timerSeconds  = totalSeconds;
  timerTotal    = totalSeconds;
  stopwatchSecs = 0;

  var modeBtns = document.querySelectorAll('.mode-btn');
  for (var i = 0; i < modeBtns.length; i++) {
    modeBtns[i].classList.remove('active');
  }
  clickedBtn.classList.add('active');

  var emoji = '⏱';
  if (label === 'Focus')       emoji = '🎯';
  if (label === 'Short Break') emoji = '☕';
  if (label === 'Long Break')  emoji = '🌿';

  document.getElementById('timer-emoji').textContent   = emoji;
  document.getElementById('timer-label').textContent   = label + ' Mode — Ready to start';
  document.getElementById('timer-display').textContent = isStopwatch ? '00:00' : formatTimerDisplay(totalSeconds);
  document.getElementById('timer-liquid').style.height = '0%';
}

function formatTimerDisplay(seconds) {
  var m = Math.floor(seconds / 60);
  var s = seconds % 60;
  return String(m).padStart(2, '0') + ':' + String(s).padStart(2, '0');
}

function updateLiquid() {
  if (isStopwatch || timerTotal === 0) return;
  var elapsed = timerTotal - timerSeconds;
  var percent = (elapsed / timerTotal) * 100;
  document.getElementById('timer-liquid').style.height = percent + '%';
}

function startTimer() {
  if (timerRunning) return;
  timerRunning = true;

  timerInterval = setInterval(function() {
    if (isStopwatch) {
      stopwatchSecs++;
      document.getElementById('timer-display').textContent = formatTimerDisplay(stopwatchSecs);
    } else {
      if (timerSeconds <= 0) {
        clearInterval(timerInterval);
        timerRunning = false;
        document.getElementById('timer-liquid').style.height = '100%';
        timerExtraMinutes += Math.floor(timerTotal / 60);
        updateTrackedStat();
        return;
      }
      timerSeconds--;
      document.getElementById('timer-display').textContent = formatTimerDisplay(timerSeconds);
      updateLiquid();
    }
  }, 1000);
}

function pauseTimer() {
  clearInterval(timerInterval);
  timerRunning = false;
}

function resetTimer() {
  clearInterval(timerInterval);
  timerRunning = false;

  if (isStopwatch) {
    stopwatchSecs = 0;
    document.getElementById('timer-display').textContent = '00:00';
  } else {
    timerSeconds = timerTotal;
    document.getElementById('timer-display').textContent = formatTimerDisplay(timerTotal);
  }
  document.getElementById('timer-liquid').style.height = '0%';
}

function updateTrackedStat() {
  var totalMins = timerExtraMinutes;

  for (var i = 0; i < tasks.length; i++) {
    if (tasks[i].status === 'done') {
      var hours = tasks[i].time.match(/(\d+)h/);
      var mins  = tasks[i].time.match(/(\d+)m/);
      if (hours) totalMins += parseInt(hours[1]) * 60;
      if (mins)  totalMins += parseInt(mins[1]);
    }
  }

  var trackedStr;
  if (totalMins >= 60) {
    trackedStr = Math.floor(totalMins / 60) + 'h';
    if (totalMins % 60 > 0) trackedStr += ' ' + (totalMins % 60) + 'm';
  } else {
    trackedStr = totalMins + 'm';
  }

  document.getElementById('stat-tracked').textContent = trackedStr;
}

function startTimerFromTop() {
  var sidebarItems = document.querySelectorAll('.sidebar-item');
  showSection('timer', sidebarItems[1]);
  setTimeout(startTimer, 100);
}

function selectMood(clickedBtn) {
  var moodBtns = document.querySelectorAll('.mood-btn');
  for (var i = 0; i < moodBtns.length; i++) {
    moodBtns[i].classList.remove('selected');
  }
  clickedBtn.classList.add('selected');
}

function saveJournalEntry() {
  var text = document.getElementById('journal-input').value.trim();
  if (text === '') return;

  var selectedMood = document.querySelector('.mood-btn.selected');
  var moodEmoji    = selectedMood ? selectedMood.textContent : '😊';
  var dateLabel    = new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });

  var card = document.createElement('div');
  card.className = 'journal-card';
  card.innerHTML =
    '<div class="journal-top">' +
      '<span class="journal-date">' + dateLabel + '</span>' +
      '<span>' + moodEmoji + '</span>' +
    '</div>' +
    '<p>' + escapeHtml(text) + '</p>' +
    '<div class="tag-row"><span class="tag">#new</span></div>';

  document.getElementById('journal-entries').prepend(card);
  document.getElementById('journal-input').value = '';
}

function initWater() {
  var row = document.getElementById('water-row');
  for (var i = 0; i < 8; i++) {
    var glass = document.createElement('div');
    glass.className = 'water-glass';

    glass.onclick = (function(g) {
      return function() { toggleWater(g); };
    })(glass);

    row.appendChild(glass);
  }
}

function toggleWater(glassEl) {
  glassEl.classList.toggle('filled');
  var filledCount = document.querySelectorAll('.water-glass.filled').length;
  document.getElementById('water-count').textContent = filledCount;
}

initWater();

function toggleExercise(itemEl) {
  itemEl.classList.toggle('done');
}

function updateSleep(value) {
  document.getElementById('sleep-display').textContent = value + 'h';

  var percent = (parseFloat(value) / 12) * 100;
  document.getElementById('sleep-fill').style.width = percent + '%';

  var hours = parseFloat(value);
  var message, color;

  if (hours >= 7) {
    message = 'Good — you got enough rest!';
    color   = '#22C08B';
  } else if (hours >= 5) {
    message = 'Okay — try to get a bit more sleep.';
    color   = '#F5A623';
  } else {
    message = 'You need more sleep. Aim for 7–9 hours.';
    color   = '#E8536A';
  }

  var msgEl = document.getElementById('sleep-msg');
  msgEl.textContent = message;
  msgEl.style.color = color;
}

if (localStorage.getItem('tasks') !== null) {
  tasks = JSON.parse(localStorage.getItem('tasks'));
}
renderTasks('all');
updateStats();