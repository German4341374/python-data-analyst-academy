import { expect, test } from "@playwright/test";

test("real learning flow rejects hardcoding and persists general solution", async ({
  page,
}) => {
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: "Большой путь начинается с print()" }),
  ).toBeVisible();
  await page.screenshot({
    path: "../docs/screenshots/dashboard.png",
    fullPage: true,
  });
  await page
    .getByRole("link", { name: "Программа обучения", exact: true })
    .click();
  await page.screenshot({
    path: "../docs/screenshots/roadmap.png",
    fullPage: true,
  });
  await page
    .getByRole("link")
    .filter({
      has: page.getByRole("heading", {
        name: "Фильтрация данных",
        exact: true,
      }),
    })
    .click();
  await expect(
    page.getByRole("heading", { name: "Фильтрация данных", exact: true }),
  ).toBeVisible();
  await page.screenshot({
    path: "../docs/screenshots/lesson.png",
    fullPage: true,
  });
  await page.getByRole("button", { name: "Урок прочитан · к квизу" }).click();
  await page
    .getByRole("radio", { name: "A df['price'] > 100", exact: true })
    .click();
  await page.getByRole("button", { name: "Проверить ответ" }).click();
  await expect(
    page.getByText("Пока не совсем. Разберёмся вместе."),
  ).toBeVisible();
  await expect(
    page.getByText("Это булева Series", { exact: false }),
  ).toBeVisible();
  await page.screenshot({
    path: "../docs/screenshots/quiz-feedback.png",
    fullPage: true,
  });
  await page.getByRole("button", { name: "Попробовать снова" }).click();
  await page
    .getByRole("radio", { name: "B df[df['price'] > 100]", exact: true })
    .click();
  await page.getByRole("button", { name: "Проверить ответ" }).click();
  await expect(page.getByText("Верно. Давайте закрепим.")).toBeVisible();
  await page.goto("/challenge/revenue-city");
  const editor = page.locator(".cm-content[contenteditable=true]");
  await editor.fill(
    "import pandas as pd\ndef revenue_by_city(df):\n    return pd.DataFrame({'city': ['Riga', 'Tallinn', 'Vilnius'], 'revenue': [480.0, 340.0, 300.0]})",
  );
  await page.getByRole("button", { name: "Запустить", exact: true }).click();
  await expect(
    page.getByText("Пример пройден · отправьте на полную проверку"),
  ).toBeVisible({ timeout: 40_000 });
  await page.getByRole("button", { name: "Отправить", exact: true }).click();
  await expect(page.getByText("Есть что улучшить")).toBeVisible({
    timeout: 90_000,
  });
  await expect(
    page.getByText("Решение не работает с новыми городами.", { exact: false }),
  ).toBeVisible();
  await editor.fill(
    "def revenue_by_city(df):\n    return (df.assign(revenue=df.quantity * df.price)\n        .groupby('city', as_index=False).agg(revenue=('revenue', 'sum'))\n        .sort_values(['revenue', 'city'], ascending=[False, True])\n        .reset_index(drop=True))",
  );
  await page.getByRole("button", { name: "Отправить", exact: true }).click();
  await expect(page.getByText("Задача решена · прогресс сохранён")).toBeVisible(
    { timeout: 90_000 },
  );
  await page.screenshot({
    path: "../docs/screenshots/pandas-challenge.png",
    fullPage: true,
  });
  await page
    .locator(".data-viewer")
    .first()
    .screenshot({ path: "../docs/screenshots/dataframe-viewer.png" });
  await page.getByRole("button", { name: /Проверки/ }).click();
  await expect(page.getByText("Скрытый набор 6")).toBeVisible();
  await page.goto("/progress");
  await expect(
    page.getByText("revenue-city", { exact: true }).first(),
  ).toBeVisible();
  await page.screenshot({
    path: "../docs/screenshots/skill-map.png",
    fullPage: true,
  });
  await page.reload();
  await expect(
    page.getByText("revenue-city", { exact: true }).first(),
  ).toBeVisible();
});

test("mobile navigation, responsive layout, and theme work", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: "Большой путь начинается с print()" }),
  ).toBeVisible();
  await expect
    .poll(() =>
      page.evaluate(
        () => document.documentElement.scrollWidth <= window.innerWidth,
      ),
    )
    .toBe(true);
  await page.screenshot({
    path: "../docs/screenshots/mobile.png",
    fullPage: true,
  });
  await page.getByRole("button", { name: "Меню", exact: true }).click();
  await page.getByRole("link", { name: "Практика", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "От знаний к навыкам" }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Светлая тема" }).click();
  await expect(page.locator("html")).toHaveAttribute("data-theme", "light");
  await page.reload();
  await expect(page.locator("html")).toHaveAttribute("data-theme", "light");
});

test("real plot rendering, playground execution and project download", async ({
  page,
}) => {
  await page.goto("/challenge/monthly-plot");
  await page
    .locator(".cm-content[contenteditable=true]")
    .fill(
      "import matplotlib.pyplot as plt\ndef plot_monthly_revenue(df):\n    monthly = df.groupby('month', as_index=False).agg(revenue=('revenue', 'sum')).sort_values('month')\n    fig, ax = plt.subplots()\n    ax.plot(monthly.month, monthly.revenue)\n    ax.set(title='Monthly revenue', xlabel='Month', ylabel='Revenue, EUR')\n    return fig\n",
    );
  await page.getByRole("button", { name: "Отправить", exact: true }).click();
  await expect(page.getByText("Задача решена · прогресс сохранён")).toBeVisible(
    { timeout: 90_000 },
  );
  await expect(page.locator("img.rendered-plot")).toBeVisible();
  expect(
    await page
      .locator("img.rendered-plot")
      .evaluate((el: HTMLImageElement) => el.naturalWidth),
  ).toBeGreaterThan(100);
  await page.screenshot({
    path: "../docs/screenshots/plot-preview.png",
    fullPage: true,
  });
  await page.goto("/playground");
  await page
    .getByRole("button", { name: "Первый Python", exact: true })
    .click();
  await page.getByRole("button", { name: "Запустить эксперимент" }).click();
  await expect(page.getByText("Выручка: 50.0", { exact: false })).toBeVisible({
    timeout: 30_000,
  });
  await page.getByRole("button", { name: "Seaborn", exact: true }).click();
  await page.getByRole("button", { name: "Запустить эксперимент" }).click();
  await expect(page.locator("img.rendered-plot")).toBeVisible({
    timeout: 30_000,
  });
  await page.screenshot({
    path: "../docs/screenshots/playground.png",
    fullPage: true,
  });
  await page.goto("/projects");
  await page.locator("a[href^='/projects/']").first().click();
  const downloadPromise = page.waitForEvent("download");
  await page.getByRole("link", { name: "Скачать ZIP" }).click();
  const download = await downloadPromise;
  expect(download.suggestedFilename()).toMatch(/\.zip$/);
  expect(await download.failure()).toBeNull();
  const checkbox = page.getByRole("checkbox").first();
  await checkbox.check();
  await page.reload();
  await expect(page.getByRole("checkbox").first()).toBeChecked();
  await page.screenshot({
    path: "../docs/screenshots/project.png",
    fullPage: true,
  });
});
