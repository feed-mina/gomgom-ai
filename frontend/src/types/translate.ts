export async function batchTranslate(texts: string[]): Promise<string[]> {
  const res = await fetch("/api/v1/translate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(texts),
  });
  const data = await res.json();
  return data.translatedTexts;
}
