export type PressToTalkRecorder = {
  start: () => Promise<void>;
  stop: () => Promise<Blob>;
};

export function createPressToTalkRecorder(): PressToTalkRecorder {
  let mediaRecorder: MediaRecorder | null = null;
  let stream: MediaStream | null = null;
  let chunks: Blob[] = [];

  return {
    async start(): Promise<void> {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      chunks = [];
      mediaRecorder = new MediaRecorder(stream, { mimeType: "audio/webm" });
      mediaRecorder.ondataavailable = (event: BlobEvent) => {
        if (event.data.size > 0) {
          chunks.push(event.data);
        }
      };
      mediaRecorder.start();
    },

    async stop(): Promise<Blob> {
      if (!mediaRecorder || mediaRecorder.state === "inactive") {
        throw new Error("Recorder is not active");
      }

      await new Promise<void>((resolve) => {
        mediaRecorder!.onstop = () => resolve();
        mediaRecorder!.stop();
      });

      stream?.getTracks().forEach((t) => t.stop());
      const blob = new Blob(chunks, { type: "audio/webm" });
      mediaRecorder = null;
      stream = null;
      chunks = [];
      return blob;
    },
  };
}

export async function playWavBytes(bytes: ArrayBuffer): Promise<void> {
  const blob = new Blob([bytes], { type: "audio/wav" });
  const url = URL.createObjectURL(blob);
  const audio = new Audio(url);
  try {
    await audio.play();
    await new Promise<void>((resolve) => {
      audio.onended = () => resolve();
      audio.onerror = () => resolve();
    });
  } finally {
    URL.revokeObjectURL(url);
  }
}
