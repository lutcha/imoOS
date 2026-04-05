"use client";

/**
 * VoiceRecorder — ImoOS Field App
 * Gravador de notas de voz (até 30 segundos)
 * Otimizado para uso com luvas em obra
 */
import { useState, useRef, useCallback } from "react";
import { Mic, Square, Play, Pause, Trash2, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";
import type { VoiceNote } from "@/types/mobile";

interface VoiceRecorderProps {
  taskId: string;
  voiceNotes: VoiceNote[];
  onVoiceNoteAdd: (note: VoiceNote) => void;
  onVoiceNoteRemove?: (noteId: string) => void;
  maxDuration?: number; // seconds
  maxNotes?: number;
}

export function VoiceRecorder({
  taskId,
  voiceNotes,
  onVoiceNoteAdd,
  onVoiceNoteRemove,
  maxDuration = 30,
  maxNotes = 5,
}: VoiceRecorderProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [processing, setProcessing] = useState(false);
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  const startRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        setProcessing(true);
        
        const audioBlob = new Blob(audioChunksRef.current, { type: "audio/webm" });
        const localUrl = URL.createObjectURL(audioBlob);
        
        const voiceNote: VoiceNote = {
          id: `voice-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          taskId,
          localUrl,
          blob: audioBlob,
          duration: recordingTime,
          timestamp: Date.now(),
          synced: false,
        };

        onVoiceNoteAdd(voiceNote);
        setProcessing(false);
        setRecordingTime(0);
        
        // Stop all tracks
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start(100); // Collect data every 100ms
      setIsRecording(true);
      
      // Start timer
      timerRef.current = setInterval(() => {
        setRecordingTime((prev) => {
          if (prev >= maxDuration) {
            stopRecording();
            return prev;
          }
          return prev + 1;
        });
      }, 1000);
      
    } catch (error) {
      console.error("Failed to start recording:", error);
      alert("Erro ao aceder ao microfone. Verifique as permissões.");
    }
  }, [taskId, onVoiceNoteAdd, maxDuration, recordingTime]);

  const stopRecording = useCallback(() => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
    
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
      mediaRecorderRef.current.stop();
    }
    
    setIsRecording(false);
  }, []);

  const canRecordMore = voiceNotes.length < maxNotes;

  return (
    <div className="w-full">
      <label className="block text-sm font-semibold text-muted-foreground uppercase tracking-wide mb-3">
        Notas de Voz ({voiceNotes.length}/{maxNotes})
      </label>

      {/* Record Button */}
      {canRecordMore && (
        <div className="mb-4">
          {!isRecording ? (
            <button
              onClick={startRecording}
              disabled={processing}
              className={cn(
                "w-full py-4 px-6 rounded-xl",
                "flex items-center justify-center gap-3",
                "bg-red-500 text-white font-semibold text-lg",
                "active:scale-[0.98] transition-transform shadow-md",
                processing && "opacity-50 cursor-not-allowed"
              )}
            >
              {processing ? (
                <>
                  <Loader2 className="w-6 h-6 animate-spin" />
                  <span>A processar...</span>
                </>
              ) : (
                <>
                  <Mic className="w-6 h-6" />
                  <span>Gravar Nota de Voz</span>
                </>
              )}
            </button>
          ) : (
            <button
              onClick={stopRecording}
              className={cn(
                "w-full py-4 px-6 rounded-xl",
                "flex items-center justify-center gap-3",
                "bg-amber-500 text-white font-semibold text-lg animate-pulse",
                "active:scale-[0.98] transition-transform shadow-md"
              )}
            >
              <Square className="w-6 h-6 fill-current" />
              <span>A gravar... {formatTime(recordingTime)} / {formatTime(maxDuration)}</span>
            </button>
          )}
          
          <p className="text-xs text-muted-foreground text-center mt-2">
            Máximo {maxDuration} segundos por nota
          </p>
        </div>
      )}

      {/* Voice Notes List */}
      <div className="space-y-2">
        {voiceNotes.map((note) => (
          <VoiceNoteItem
            key={note.id}
            note={note}
            onRemove={onVoiceNoteRemove}
          />
        ))}
      </div>
    </div>
  );
}

function VoiceNoteItem({
  note,
  onRemove,
}: {
  note: VoiceNote;
  onRemove?: (id: string) => void;
}) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const togglePlay = () => {
    if (!audioRef.current) {
      audioRef.current = new Audio(note.localUrl);
      audioRef.current.onended = () => setIsPlaying(false);
      audioRef.current.ontimeupdate = () => {
        setCurrentTime(Math.floor(audioRef.current?.currentTime || 0));
      };
    }

    if (isPlaying) {
      audioRef.current.pause();
      setIsPlaying(false);
    } else {
      audioRef.current.play();
      setIsPlaying(true);
    }
  };

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  return (
    <div className="flex items-center gap-3 p-3 bg-white rounded-xl border border-border">
      <button
        onClick={togglePlay}
        className={cn(
          "w-12 h-12 rounded-full flex items-center justify-center flex-shrink-0",
          isPlaying ? "bg-amber-500 text-white" : "bg-primary text-primary-foreground"
        )}
      >
        {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5 ml-0.5" />}
      </button>

      <div className="flex-1 min-w-0">
        <p className="font-medium text-sm">
          Nota de voz {new Date(note.timestamp).toLocaleTimeString("pt-CV", { hour: "2-digit", minute: "2-digit" })}
        </p>
        <p className="text-xs text-muted-foreground">
          {isPlaying ? formatTime(currentTime) : formatTime(note.duration)}
        </p>
        {!note.synced && (
          <span className="text-xs text-amber-600">⏳ Pendente sincronizar</span>
        )}
      </div>

      {onRemove && (
        <button
          onClick={() => onRemove(note.id)}
          className="p-2 text-red-500 hover:bg-red-50 rounded-lg transition-colors"
          aria-label="Remover nota"
        >
          <Trash2 className="w-5 h-5" />
        </button>
      )}
    </div>
  );
}
