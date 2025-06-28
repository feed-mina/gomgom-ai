export async function batchTranslate(texts: string[]): Promise<string[]> {
  // 빈 텍스트 필터링
  const validTexts = texts.filter(text => text && text.trim());
  
  if (validTexts.length === 0) {
    return [];
  }

  // 청크 크기 설정 (한 번에 처리할 텍스트 개수)
  const CHUNK_SIZE = 10;
  const chunks: string[][] = [];
  
  // 텍스트를 청크로 분할
  for (let i = 0; i < validTexts.length; i += CHUNK_SIZE) {
    chunks.push(validTexts.slice(i, i + CHUNK_SIZE));
  }

  console.log(`번역 요청: ${validTexts.length}개 텍스트를 ${chunks.length}개 청크로 분할`);

  try {
    // 각 청크를 병렬로 번역
    const chunkPromises = chunks.map(async (chunk, index) => {
      console.log(`청크 ${index + 1}/${chunks.length} 번역 시작 (${chunk.length}개 텍스트)`);
      
      const res = await fetch("/api/v1/translate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(chunk),
      });

      if (!res.ok) {
        console.error(`청크 ${index + 1} 번역 실패:`, res.status, res.statusText);
        // 실패 시 원본 텍스트 반환
        return chunk;
      }

      const data = await res.json();
      console.log(`청크 ${index + 1}/${chunks.length} 번역 완료`);
      return data.translatedTexts || chunk;
    });

    // 모든 청크 번역 완료 대기
    const chunkResults = await Promise.all(chunkPromises);
    
    // 결과를 하나의 배열로 합치기
    const allResults = chunkResults.flat();
    
    console.log(`전체 번역 완료: ${allResults.length}개 텍스트`);
    return allResults;

  } catch (error) {
    console.error('번역 중 오류 발생:', error);
    // 오류 발생 시 원본 텍스트 반환
    return validTexts;
  }
}
