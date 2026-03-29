(function setupPythonQuestRuntime(window) {
  const OFFLINE_PROTOCOLS = new Set(["app:"]);

  function isOfflineRuntime() {
    return typeof window !== "undefined" && OFFLINE_PROTOCOLS.has(window.location.protocol);
  }

  function absoluteURL(relativePath) {
    return new URL(relativePath, window.location.href).toString();
  }

  function wrapText(text, width = 68, indent = "    ") {
    const words = String(text || "").trim().split(/\s+/).filter(Boolean);
    if (!words.length) {
      return `${indent}${String(text || "").trim()}`.trimEnd();
    }

    const lines = [];
    let current = "";

    words.forEach((word) => {
      const candidate = current ? `${current} ${word}` : word;
      if (candidate.length > width && current) {
        lines.push(`${indent}${current}`);
        current = word;
      } else {
        current = candidate;
      }
    });

    if (current) {
      lines.push(`${indent}${current}`);
    }

    return lines.join("\n");
  }

  function formatCodeBlock(code, label) {
    const lines = String(code || "")
      .split("\n")
      .map((line) => `    ${label}${line}`);
    return lines.join("\n");
  }

  function fetchJsonOrThrow(url, options) {
    return fetch(url, options).then(async (response) => {
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload?.detail || `Request failed (${response.status})`);
      }
      return payload;
    });
  }

  function createNetworkClient() {
    return {
      isOffline: false,
      fetchSections() {
        return fetchJsonOrThrow("/api/sections");
      },
      fetchQuestCatalog() {
        return fetchJsonOrThrow("/api/python-quest");
      },
      validateQuest(lessonSlug, challengeIndex, code) {
        return fetchJsonOrThrow("/api/python-quest/validate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            lesson_slug: lessonSlug,
            challenge_index: challengeIndex,
            code,
          }),
        });
      },
      getPythonStatus() {
        return fetchJsonOrThrow("/api/python-cli/status");
      },
      createPythonSession() {
        return fetchJsonOrThrow("/api/python-cli/sessions", { method: "POST" });
      },
      readPythonOutput(sessionId, cursor) {
        return fetchJsonOrThrow(`/api/python-cli/sessions/${sessionId}/output?cursor=${cursor}`);
      },
      sendPythonInput(sessionId, text) {
        return fetchJsonOrThrow(`/api/python-cli/sessions/${sessionId}/input`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text }),
        });
      },
      deletePythonSession(sessionId) {
        return fetch(`/api/python-cli/sessions/${sessionId}`, { method: "DELETE" }).catch(() => null);
      },
    };
  }

  class OfflinePythonExecutor {
    constructor() {
      this.worker = null;
      this.requestId = 0;
      this.pending = new Map();
    }

    ensureWorker() {
      if (this.worker) {
        return this.worker;
      }

      const worker = new Worker(absoluteURL("./offline-python-worker.js"));
      worker.onmessage = (event) => {
        const message = event.data || {};
        const pending = this.pending.get(message.id);
        if (!pending) {
          return;
        }

        this.pending.delete(message.id);
        if (message.ok) {
          pending.resolve(message.payload);
          return;
        }

        pending.reject(new Error(message.error || "Python worker request failed"));
      };
      worker.onerror = (event) => {
        const message = event?.message || "Python worker crashed";
        this.resetWorker(new Error(message));
      };

      this.worker = worker;
      return worker;
    }

    resetWorker(error) {
      if (this.worker) {
        this.worker.terminate();
        this.worker = null;
      }

      this.pending.forEach(({ reject, timer }) => {
        window.clearTimeout(timer);
        reject(error || new Error("Python worker reset"));
      });
      this.pending.clear();
    }

    call(type, payload, timeoutMs = 4000) {
      const worker = this.ensureWorker();
      const id = `worker-${++this.requestId}`;

      return new Promise((resolve, reject) => {
        const timer = window.setTimeout(() => {
          this.pending.delete(id);
          this.resetWorker(new Error("Python execution timed out"));
          reject(new Error("Python execution timed out"));
        }, timeoutMs);

        this.pending.set(id, {
          resolve: (value) => {
            window.clearTimeout(timer);
            resolve(value);
          },
          reject: (error) => {
            window.clearTimeout(timer);
            reject(error);
          },
          timer,
        });

        worker.postMessage({ id, type, payload });
      });
    }

    validateChallenge(challenge, code, lessonSlug) {
      return this.call("validate", { challenge, code, lessonSlug });
    }
  }

  class OfflineLessonSession {
    constructor(lessons, executor) {
      this.lessons = lessons;
      this.executor = executor;
      this.buffer = "";
      this.alive = true;
      this.mode = "boot";
      this.currentLessonIndex = -1;
      this.learnSteps = [];
      this.learnStepIndex = 0;
      this.quizQuestions = [];
      this.quizIndex = 0;
      this.quizCorrect = 0;
      this.practiceChallenges = [];
      this.practiceIndex = 0;
      this.practiceScore = 0;
      this.practiceLines = [];
      this.append(this.renderMainMenu());
      this.mode = "main-menu";
    }

    get cursor() {
      return this.buffer.length;
    }

    currentLesson() {
      return this.lessons[this.currentLessonIndex] || null;
    }

    append(text) {
      this.buffer += String(text || "");
    }

    read(cursor) {
      const boundedCursor = Math.max(0, Math.min(Number(cursor) || 0, this.buffer.length));
      return {
        output: this.buffer.slice(boundedCursor),
        cursor: this.buffer.length,
        alive: this.alive,
      };
    }

    close() {
      this.alive = false;
    }

    renderMainMenu() {
      const rows = this.lessons
        .map((lesson, index) => `  ${String(index + 1).padStart(2)}.   ${lesson.title}`)
        .join("\n");
      return `\n${"=".repeat(60)}\n  Python Interactive Learning\n${"=".repeat(60)}\n\n${rows}\n\n   q. Quit\n\n  Pick a lesson (1-10) or 'q' to quit: `;
    }

    renderLessonMenu(lesson) {
      return `\n${"=".repeat(60)}\n  ${lesson.menu_title || lesson.title}\n${"=".repeat(60)}\n\n  [L] Learn - Read concepts with live examples\n  [P] Practice - Solve coding challenges\n  [Q] Quiz - Test your knowledge\n  [B] Back to main menu\n\n  Choose mode: `;
    }

    buildLearnSteps(lesson) {
      return (lesson.learn_cards || []).map((card) => {
        if (card.kind === "checkpoint") {
          return `\n--- ${card.title} ---\n`;
        }

        if (card.kind === "concept") {
          return `\n  [${card.title}]\n${wrapText(card.body || "")}\n`;
        }

        if (card.kind === "code") {
          return `\n  Code:\n${formatCodeBlock(card.code || "", ">>> ")}\n  Output:\n${formatCodeBlock(card.output || "", "")}\n`;
        }

        return "";
      });
    }

    showNextLearnStep() {
      if (this.learnStepIndex >= this.learnSteps.length) {
        this.append("\n  Learn section complete. Try Practice or Quiz next.\n");
        const lesson = this.currentLesson();
        if (lesson) {
          this.append(this.renderLessonMenu(lesson));
          this.mode = "lesson-menu";
        }
        return;
      }

      this.append(this.learnSteps[this.learnStepIndex]);
      this.learnStepIndex += 1;
      this.mode = "learn-await-continue";
      this.append(
        this.learnStepIndex >= this.learnSteps.length
          ? "\n  Press Enter to return to the lesson menu..."
          : "\n  Press Enter to continue...",
      );
    }

    showQuizQuestion() {
      const question = this.quizQuestions[this.quizIndex];
      if (!question) {
        const total = this.quizQuestions.length;
        this.append(`\n  Score: ${this.quizCorrect}/${total}\n`);
        if (this.quizCorrect === total) {
          this.append("  Perfect score! You nailed it!\n");
        } else if (this.quizCorrect >= total * 0.7) {
          this.append("  Great job! You're getting the hang of it!\n");
        } else {
          this.append("  Keep practicing! Review the learn section and try again.\n");
        }

        const lesson = this.currentLesson();
        if (lesson) {
          this.append(this.renderLessonMenu(lesson));
          this.mode = "lesson-menu";
        }
        return;
      }

      const options = (question.options || [])
        .map((option, index) => `    ${String.fromCharCode(65 + index)}) ${option}`)
        .join("\n");
      this.append(
        `\n  Question ${this.quizIndex + 1}/${this.quizQuestions.length}:\n  ${question.question}\n\n${options}\n\n  Your answer (A/B/C/D): `,
      );
      this.mode = "quiz-await-answer";
    }

    showPracticeChallenge() {
      const challenge = this.practiceChallenges[this.practiceIndex];
      if (!challenge) {
        this.append(`\n  Score: ${this.practiceScore}/${this.practiceChallenges.length}\n\n`);
        const lesson = this.currentLesson();
        if (lesson) {
          this.append(this.renderLessonMenu(lesson));
          this.mode = "lesson-menu";
        }
        return;
      }

      if (this.practiceIndex === 0) {
        this.append("\n--- Coding Challenges ---\n");
      }

      this.append(
        `\n  Challenge ${this.practiceIndex + 1}/${this.practiceChallenges.length}:\n  ${challenge.prompt}\n\n`,
      );

      if (challenge.hint) {
        this.mode = "practice-await-hint";
        this.append("  Need a hint? (y/n): ");
        return;
      }

      this.practiceLines = [];
      this.mode = "practice-await-code";
      this.append("  Type your code (press Enter twice to submit):\n");
    }

    async handleMainMenuInput(text) {
      const normalized = String(text || "").trim().toLowerCase();
      if (normalized === "q") {
        this.append("\n  Happy learning! See you next time.\n");
        this.alive = false;
        this.mode = "ended";
        return;
      }

      const lessonNumber = Number.parseInt(normalized, 10);
      if (!Number.isNaN(lessonNumber) && lessonNumber >= 1 && lessonNumber <= this.lessons.length) {
        this.currentLessonIndex = lessonNumber - 1;
        this.append(this.renderLessonMenu(this.currentLesson()));
        this.mode = "lesson-menu";
        return;
      }

      this.append("\n  Invalid input. Enter a number or 'q'.");
      this.append(this.renderMainMenu());
      this.mode = "main-menu";
    }

    async handleLessonMenuInput(text) {
      const normalized = String(text || "").trim().toUpperCase();
      const lesson = this.currentLesson();
      if (!lesson) {
        this.append(this.renderMainMenu());
        this.mode = "main-menu";
        return;
      }

      if (normalized === "B") {
        this.append(this.renderMainMenu());
        this.mode = "main-menu";
        return;
      }

      if (normalized === "L") {
        this.learnSteps = this.buildLearnSteps(lesson);
        this.learnStepIndex = 0;
        this.showNextLearnStep();
        return;
      }

      if (normalized === "Q") {
        this.quizQuestions = (lesson.quiz || []).slice();
        this.quizIndex = 0;
        this.quizCorrect = 0;
        this.showQuizQuestion();
        return;
      }

      if (normalized === "P") {
        this.practiceChallenges = (lesson.practice_full || []).slice();
        this.practiceIndex = 0;
        this.practiceScore = 0;
        this.showPracticeChallenge();
        return;
      }

      this.append("\n  Invalid choice. Try L, P, Q, or B.");
      this.append(this.renderLessonMenu(lesson));
      this.mode = "lesson-menu";
    }

    async handleQuizInput(text) {
      const question = this.quizQuestions[this.quizIndex];
      if (!question) {
        return;
      }

      const answer = String(text || "").trim().toUpperCase();
      const correctLabel = String.fromCharCode(65 + question.answer);
      if (answer === correctLabel) {
        this.quizCorrect += 1;
        this.append("\n  Correct!\n");
      } else {
        this.append(`\n  Wrong! The answer is ${correctLabel}) ${question.options[question.answer]}\n`);
        if (question.explanation) {
          this.append(`  Why: ${question.explanation}\n`);
        }
      }

      this.quizIndex += 1;
      this.showQuizQuestion();
    }

    async finishPracticeSubmission() {
      const challenge = this.practiceChallenges[this.practiceIndex];
      const code = this.practiceLines.join("\n");

      try {
        const result = await this.executor.validateChallenge(
          challenge,
          code,
          this.currentLesson()?.slug || "offline",
        );

        if (result.ok) {
          this.practiceScore += 1;
          this.append("  Correct! Well done!\n");
        } else {
          this.append(`  ${result.message}\n`);
          if (challenge.solution) {
            this.append(`  Example solution:\n${formatCodeBlock(challenge.solution, "")}\n`);
          }
        }

        if (result.stdout) {
          this.append(`  Output:\n${formatCodeBlock(result.stdout, "")}\n`);
        }
      } catch (error) {
        this.append(`  ${error instanceof Error ? error.message : String(error)}\n`);
        if (challenge.solution) {
          this.append(`  Example solution:\n${formatCodeBlock(challenge.solution, "")}\n`);
        }
      }

      this.practiceIndex += 1;
      this.showPracticeChallenge();
    }

    async handlePracticeHintInput(text) {
      const challenge = this.practiceChallenges[this.practiceIndex];
      if (String(text || "").trim().toLowerCase() === "y" && challenge?.hint) {
        this.append(`\n  Hint: ${challenge.hint}\n\n`);
      } else {
        this.append("\n");
      }

      this.practiceLines = [];
      this.mode = "practice-await-code";
      this.append("  Type your code (press Enter twice to submit):\n");
    }

    async handlePracticeCodeInput(text) {
      const line = String(text ?? "");
      if (line === "") {
        if (!this.practiceLines.length) {
          return;
        }

        this.append("\n");
        await this.finishPracticeSubmission();
        return;
      }

      this.practiceLines.push(line);
    }

    async handleInput(text) {
      if (!this.alive) {
        return;
      }

      switch (this.mode) {
        case "main-menu":
          await this.handleMainMenuInput(text);
          return;
        case "lesson-menu":
          await this.handleLessonMenuInput(text);
          return;
        case "learn-await-continue":
          this.append("\n");
          this.showNextLearnStep();
          return;
        case "quiz-await-answer":
          await this.handleQuizInput(text);
          return;
        case "practice-await-hint":
          await this.handlePracticeHintInput(text);
          return;
        case "practice-await-code":
          await this.handlePracticeCodeInput(text);
          return;
        default:
          return;
      }
    }
  }

  class OfflineClient {
    constructor() {
      this.isOffline = true;
      this.sectionsPromise = null;
      this.lessonsPromise = null;
      this.sessions = new Map();
      this.nextSessionId = 1;
      this.executor = new OfflinePythonExecutor();
    }

    loadSections() {
      if (!this.sectionsPromise) {
        this.sectionsPromise = fetch(absoluteURL("./data/question_bank.json")).then((response) =>
          response.json(),
        );
      }
      return this.sectionsPromise;
    }

    loadLessons() {
      if (!this.lessonsPromise) {
        this.lessonsPromise = fetch(absoluteURL("./data/offline_python_lessons.json")).then(
          (response) => response.json(),
        );
      }
      return this.lessonsPromise;
    }

    async fetchSections() {
      return this.loadSections();
    }

    async fetchQuestCatalog() {
      return this.loadLessons();
    }

    async validateQuest(lessonSlug, challengeIndex, code) {
      const payload = await this.loadLessons();
      const lesson = (payload.lessons || []).find((item) => item.slug === lessonSlug);
      const challenge = lesson?.practice_full?.[challengeIndex];
      if (!lesson || !challenge) {
        throw new Error("Quest challenge not found in on-device mode");
      }
      return this.executor.validateChallenge(challenge, code, lessonSlug);
    }

    async getPythonStatus() {
      return {
        available: true,
        module_exists: true,
        reason: "Runs entirely on your iPhone with the bundled Python engine.",
      };
    }

    async createPythonSession() {
      const payload = await this.loadLessons();
      const sessionId = `offline-${this.nextSessionId++}`;
      const session = new OfflineLessonSession(payload.lessons || [], this.executor);
      this.sessions.set(sessionId, session);
      return {
        session_id: sessionId,
        cursor: session.cursor,
        output: session.buffer,
      };
    }

    async readPythonOutput(sessionId, cursor) {
      const session = this.sessions.get(sessionId);
      if (!session) {
        throw new Error("Python CLI session not found");
      }
      const payload = session.read(cursor);
      if (!payload.alive && payload.cursor >= session.cursor) {
        this.sessions.delete(sessionId);
      }
      return payload;
    }

    async sendPythonInput(sessionId, text) {
      const session = this.sessions.get(sessionId);
      if (!session) {
        throw new Error("Python CLI session not found");
      }

      await session.handleInput(text);
      return { ok: true };
    }

    async deletePythonSession(sessionId) {
      const session = this.sessions.get(sessionId);
      if (session) {
        session.close();
        this.sessions.delete(sessionId);
      }
      return { ok: true };
    }
  }

  window.PythonQuestRuntimeClient = {
    createClient() {
      return isOfflineRuntime() ? new OfflineClient() : createNetworkClient();
    },
    isOfflineRuntime,
  };
})(window);
