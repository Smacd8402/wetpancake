export type AudioChunk = {
  pcm: ArrayBuffer;
  sampleRate: number;
};

export async function getMicrophoneStream(): Promise<MediaStream> {
  return navigator.mediaDevices.getUserMedia({ audio: true });
}
