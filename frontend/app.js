const form = document.querySelector("#analytics-form");
const results = document.querySelector("#results");
const message = document.querySelector("#message");
const submitButton = form.querySelector("button");
const serviceStatus = document.querySelector("#service-status");

const setText = (id, value) => {
  document.querySelector(`#${id}`).textContent = value ?? "—";
};

const wait = (milliseconds) => new Promise((resolve) => {
  setTimeout(resolve, milliseconds);
});

async function readJson(response) {
  const body = await response.json();
  if (!response.ok) {
    throw new Error(body.detail || "Не удалось выполнить запрос");
  }
  return body;
}

async function waitForJob(jobId) {
  const deadline = Date.now() + 60_000;

  while (Date.now() < deadline) {
    const job = await readJson(
      await fetch(`/api/analytics/jobs/${jobId}`, { cache: "no-store" }),
    );

    if (job.status === "done") return job.result;
    if (job.status === "failed") {
      throw new Error(job.error || "Расчёт завершился с ошибкой");
    }

    message.textContent = job.status === "running"
      ? "Worker обрабатывает данные…"
      : "Задание ожидает обработки в RabbitMQ…";

    await wait(1_000);
  }

  throw new Error("Расчёт занимает слишком много времени. Попробуйте ещё раз.");
}

fetch("/api/health")
  .then((response) => {
    if (!response.ok) throw new Error();
    serviceStatus.lastChild.textContent = " Analytics online";
  })
  .catch(() => {
    serviceStatus.lastChild.textContent = " Analytics offline";
    serviceStatus.classList.add("offline");
  });

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  message.textContent = "";
  submitButton.disabled = true;
  submitButton.firstChild.textContent = "Загружаем… ";

  const formData = new FormData(form);

  try {
    const job = await readJson(await fetch("/api/analytics/jobs", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        team: formData.get("team"),
        season: formData.get("season"),
      }),
    }));

    message.textContent = "Задание отправлено в RabbitMQ…";
    const body = await waitForJob(job.job_id);

    setText("rain-matches", body.rain.matches);
    setText("rain-goals", body.rain.avg_goals);
    setText("rain-xg", body.rain.avg_xg);
    setText("dry-matches", body.dry.matches);
    setText("dry-goals", body.dry.avg_goals);
    setText("dry-xg", body.dry.avg_xg);

    document.querySelector("#result-meta").textContent =
      `${body.team} · ${body.season} · ${body.matches_total} матчей · job ${job.job_id.slice(0, 8)}`;

    message.textContent = "";
    results.hidden = false;
    results.scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (error) {
    message.textContent = error.message === "Failed to fetch"
      ? "Сервис аналитики недоступен. Проверьте, запущен ли Docker Compose."
      : error.message;
  } finally {
    submitButton.disabled = false;
    submitButton.firstChild.textContent = "Провести анализ ";
  }
});
