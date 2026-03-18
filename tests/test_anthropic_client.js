// tests/test_anthropic_client.js

const url = 'http://localhost:8000/api/v1/messages';

async function sseClient() {
  const res = await fetch(url, {
    method: 'GET',
    headers: {
      Accept: 'text/event-stream',
    },
  });

  if (!res.ok) {
    console.error('HTTP error', res.status, await res.text());
    return;
  }

  if (!res.body) {
    console.error('No response body (stream not supported?)');
    return;
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder('utf-8');

  let buffer = '';

  console.log('SSE connection opened:', url);

  while (true) {
    const { value, done } = await reader.read();
    if (done) {
      console.log('SSE stream closed by server');
      break;
    }

    buffer += decoder.decode(value, { stream: true });

    let lines = buffer.split('\n');
    buffer = lines.pop() || ''; // 把最后一行不完整的留到下一轮

    for (const line of lines) {
      const trimmed = line.trim();

      // SSE 注释/心跳行
      if (trimmed === '' || trimmed.startsWith(':')) continue;

      // 只简单处理 "data:" 行
      if (trimmed.startsWith('data:')) {
        const dataStr = trimmed.slice(5).trim();
        try {
          const data = JSON.parse(dataStr);
          console.log('Received item:', data);
        } catch {
          console.log('Received raw data:', dataStr);
        }
      }
    }
  }
}

if (typeof fetch === 'undefined') {
  console.error('Global fetch is not available. Use Node 18+ 或自行引入 fetch 实现。');
} else {
  sseClient().catch((err) => {
    console.error('SSE client error:', err);
  });
}