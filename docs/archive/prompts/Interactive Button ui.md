now i ill give u some changes for specific button below :

for ""**DRAG & DROP EVIDENCE IMAGE OR CLICK TO SELECT (JPG, PNG, WEBP)**  ""


"use client";

import {
  FileArrowUpIcon,
  ImageSquareIcon,
  CheckCircleIcon,
  UploadSimpleIcon,
  XIcon,
} from "@phosphor-icons/react";
import {
  motion,
  useMotionValue,
  useReducedMotion,
  useSpring,
} from "motion/react";
import {
  useCallback,
  useEffect,
  useRef,
  useState,
  type ChangeEvent,
  type DragEvent,
} from "react";

type MagneticDropZoneProps = {
  onFilesChange?: (files: File[]) => void;
  maxSize?: number;
  className?: string;
};

const ACCEPTED_TYPES = new Set([
  "image/jpeg",
  "image/png",
  "image/webp",
]);

const ACCEPTED_EXTENSIONS = /\.(jpe?g|png|webp)$/i;

const formatBytes = (bytes: number) => {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024)
    return `${(bytes / 1024).toFixed(1)} KB`;

  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
};

export function MagneticDropZone({
  onFilesChange,
  maxSize = 20 * 1024 * 1024,
  className = "",
}: MagneticDropZoneProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const zoneRef = useRef<HTMLDivElement>(null);

  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState("");
  const [isOver, setIsOver] = useState(false);
  const [isNear, setIsNear] = useState(false);

  const reducedMotion = useReducedMotion();

  const targetX = useMotionValue(0);
  const targetY = useMotionValue(0);
  const x = useSpring(targetX, {
    stiffness: 260,
    damping: 24,
    mass: 0.6,
  });
  const y = useSpring(targetY, {
    stiffness: 260,
    damping: 24,
    mass: 0.6,
  });

  const resetMagnet = useCallback(() => {
    targetX.set(0);
    targetY.set(0);
    setIsNear(false);
    setIsOver(false);
  }, [targetX, targetY]);

  const handleFiles = useCallback(
    (files: FileList | File[]) => {
      const selected = Array.from(files)[0];

      if (!selected) return;

      if (
        !ACCEPTED_TYPES.has(selected.type) ||
        !ACCEPTED_EXTENSIONS.test(selected.name)
      ) {
        setError("Unsupported file. Use JPG, PNG, or WEBP.");
        return;
      }

      if (selected.size === 0) {
        setError("The selected file is empty.");
        return;
      }

      if (selected.size > maxSize) {
        setError(
          `Image exceeds the ${formatBytes(maxSize)} size limit.`
        );
        return;
      }

      setFile(selected);
      setError("");
      onFilesChange?.([selected]);
    },
    [maxSize, onFilesChange]
  );

  const handleInputChange = (
    event: ChangeEvent<HTMLInputElement>
  ) => {
    if (event.target.files) {
      handleFiles(event.target.files);
    }

    // Allow selecting the same file again.
    event.target.value = "";
  };

  const handleDrop = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    handleFiles(event.dataTransfer.files);
    resetMagnet();
  };

  const handleDragOver = (
    event: DragEvent<HTMLDivElement>
  ) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = "copy";
    setIsOver(true);
    setIsNear(true);
  };

  const handleDragLeave = (
    event: DragEvent<HTMLDivElement>
  ) => {
    if (
      event.currentTarget.contains(event.relatedTarget as Node)
    ) {
      return;
    }

    setIsOver(false);
  };

  useEffect(() => {
    if (reducedMotion) return;

    const handleWindowDrag = (event: globalThis.DragEvent) => {
      if (
        !Array.from(event.dataTransfer?.types ?? []).includes(
          "Files"
        )
      ) {
        return;
      }

      const zone = zoneRef.current;
      if (!zone) return;

      const rect = zone.getBoundingClientRect();
      const centerX = rect.left + rect.width / 2;
      const centerY = rect.top + rect.height / 2;

      const dx = event.clientX - centerX;
      const dy = event.clientY - centerY;

      const outsideX = Math.max(
        Math.abs(dx) - rect.width / 2,
        0
      );
      const outsideY = Math.max(
        Math.abs(dy) - rect.height / 2,
        0
      );

      const distance = Math.hypot(outsideX, outsideY);
      const radius = 180;

      if (distance > radius) {
        resetMagnet();
        return;
      }

      const proximity = 1 - distance / radius;
      const pointerDistance = Math.max(Math.hypot(dx, dy), 1);
      const offset = proximity * 9;

      targetX.set((dx / pointerDistance) * offset);
      targetY.set((dy / pointerDistance) * offset);
      setIsNear(true);
    };

    window.addEventListener("dragover", handleWindowDrag);
    window.addEventListener("dragend", resetMagnet);
    window.addEventListener("drop", resetMagnet);

    return () => {
      window.removeEventListener("dragover", handleWindowDrag);
      window.removeEventListener("dragend", resetMagnet);
      window.removeEventListener("drop", resetMagnet);
    };
  }, [reducedMotion, resetMagnet, targetX, targetY]);

  const removeFile = () => {
    setFile(null);
    setError("");
    onFilesChange?.([]);
  };

  return (
    <motion.div
      ref={zoneRef}
      style={reducedMotion ? undefined : { x, y }}
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      className={[
        "relative w-full overflow-hidden rounded-xl border",
        "bg-[#0e131b] p-6 text-center text-[#e7edf5]",
        "transition-colors duration-200",
        isOver
          ? "border-[#ff654f] bg-[#171923]"
          : isNear
            ? "border-[#737f94]"
            : "border-[#303846]",
        className,
      ].join(" ")}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".jpg,.jpeg,.png,.webp,image/jpeg,image/png,image/webp"
        className="hidden"
        onChange={handleInputChange}
        aria-label="Choose evidence image"
      />

      {/* Ambient glow */}
      <div
        aria-hidden="true"
        className={[
          "pointer-events-none absolute inset-0",
          "bg-[radial-gradient(ellipse_at_center,rgba(255,101,79,0.12),transparent_65%)]",
          "transition-opacity duration-300",
          isNear ? "opacity-100" : "opacity-0",
        ].join(" ")}
      />

      <div className="relative z-10 flex flex-col items-center">
        {file ? (
          <>
            <div className="flex size-12 items-center justify-center rounded-xl border border-emerald-500/30 bg-emerald-500/10 text-emerald-400">
              <CheckCircleIcon size={26} weight="fill" />
            </div>

            <p className="mt-4 text-sm font-semibold">
              Evidence ready
            </p>

            <p className="mt-2 max-w-full truncate text-sm text-[#aab5c5]">
              {file.name}
            </p>

            <p className="mt-1 font-mono text-xs text-[#8491a4]">
              {formatBytes(file.size)}
            </p>

            <div className="mt-5 flex flex-wrap justify-center gap-2">
              <button
                type="button"
                onClick={() => inputRef.current?.click()}
                className="inline-flex h-9 items-center gap-2 rounded-lg border border-[#394354] px-3 text-xs font-medium hover:bg-white/5 focus-visible:outline-2 focus-visible:outline-[#ff654f]"
              >
                <UploadSimpleIcon size={15} />
                Replace
              </button>

              <button
                type="button"
                onClick={removeFile}
                className="inline-flex h-9 items-center gap-2 rounded-lg border border-[#394354] px-3 text-xs font-medium hover:bg-white/5 focus-visible:outline-2 focus-visible:outline-[#ff654f]"
              >
                <XIcon size={15} />
                Remove
              </button>
            </div>
          </>
        ) : (
          <>
            <div
              className={[
                "flex size-14 items-center justify-center rounded-xl border",
                "transition-colors duration-200",
                isOver
                  ? "border-[#ff654f]/60 bg-[#ff654f]/10 text-[#ff765f]"
                  : "border-[#394354] bg-[#171d27] text-[#aab5c5]",
              ].join(" ")}
            >
              <FileArrowUpIcon size={28} weight="duotone" />
            </div>

            <p className="mt-4 text-sm font-semibold">
              {isOver
                ? "Release to upload evidence"
                : "Drag & drop evidence image"}
            </p>

            <p className="mt-2 text-xs text-[#929eb0]">
              or click below to browse your files
            </p>

            <button
              type="button"
              onClick={() => inputRef.current?.click()}
              className="mt-5 inline-flex h-10 items-center gap-2 rounded-lg border border-[#ff654f]/40 bg-[#ff654f]/10 px-4 text-sm font-medium text-[#ff806b] transition-colors hover:border-[#ff654f] hover:bg-[#ff654f]/15 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#ff654f]"
            >
              <ImageSquareIcon size={17} />
              Select evidence
            </button>

            <p className="mt-4 font-mono text-[10px] uppercase tracking-[0.12em] text-[#758196]">
              JPG · PNG · WEBP · Max {formatBytes(maxSize)}
            </p>
          </>
        )}

        {error && (
          <p
            role="alert"
            className="mt-4 text-xs text-[#ff806b]"
          >
            {error}
          </p>
        )}
      </div>
    </motion.div>
  );
}



- use magnetic drop zone



for ""ELA DIFFERENCE , TAMPER HEATMAP , AI ATTRIBUTION , ""



- use tactical buttons



import { ArrowRightIcon } from "@phosphor-icons/react/dist/ssr";
import { TactileButton } from "@/components/TactileButton";

export function TactileButtonShowcase() {
  return (
    <div className="flex min-h-80 w-full items-center justify-center rounded-[13px] bg-grayscale-2">
      <TactileButton size="sm">
        <span>Continue</span>
        <ArrowRightIcon aria-hidden="true" size={14} weight="bold" />
      </TactileButton>
    </div>
  );
}\

for ""EXPORT FORENSIC REPORTS ""

- use Hold to Confirm

"use client";

import { CheckIcon } from "@phosphor-icons/react/dist/ssr";
import { useReducedMotion } from "motion/react";
import {
  type ComponentPropsWithoutRef,
  type KeyboardEvent,
  type PointerEvent,
  type ReactNode,
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";
import { cn } from "@/helpers/classname-helper";

type HoldToConfirmButtonProps = Omit<
  ComponentPropsWithoutRef<"button">,
  "children" | "onClick"
> & {
  children?: ReactNode;
  confirmedContent?: ReactNode;
  duration?: number;
  onConfirm: (input: ConfirmationInput) => void;
  resetAfter?: number;
};

type HoldStatus = "confirmed" | "holding" | "idle";
export type ConfirmationInput = "keyboard" | "pointer";

export function HoldToConfirmButton({
  children = "Hold to confirm",
  className,
  confirmedContent,
  disabled,
  duration = 1600,
  onConfirm,
  resetAfter = 1800,
  ...buttonProps
}: HoldToConfirmButtonProps) {
  const buttonRef = useRef<HTMLButtonElement>(null);
  const confirmTimerRef = useRef<number | null>(null);
  const resetTimerRef = useRef<number | null>(null);
  const activePointerIdRef = useRef<number | null>(null);
  const inputModeRef = useRef<ConfirmationInput>("pointer");
  const isHoldingRef = useRef(false);
  const [inputMode, setInputMode] = useState<ConfirmationInput | null>(null);
  const [status, setStatus] = useState<HoldStatus>("idle");
  const shouldReduceMotion = useReducedMotion();

  const clearConfirmTimer = useCallback(() => {
    if (confirmTimerRef.current === null) {
      return;
    }

    window.clearTimeout(confirmTimerRef.current);
    confirmTimerRef.current = null;
  }, []);

  const completeHold = useCallback(() => {
    if (!isHoldingRef.current) {
      return;
    }

    isHoldingRef.current = false;
    activePointerIdRef.current = null;
    clearConfirmTimer();
    setStatus("confirmed");
    onConfirm(inputModeRef.current);

    if (resetAfter > 0) {
      resetTimerRef.current = window.setTimeout(() => {
        setStatus("idle");
        resetTimerRef.current = null;
      }, resetAfter);
    }
  }, [clearConfirmTimer, onConfirm, resetAfter]);

  const cancelHold = useCallback(() => {
    if (!isHoldingRef.current) {
      return;
    }

    isHoldingRef.current = false;
    activePointerIdRef.current = null;
    clearConfirmTimer();
    setStatus("idle");
  }, [clearConfirmTimer]);

  const startHold = useCallback(
    (input: ConfirmationInput) => {
      if (disabled || status === "confirmed" || isHoldingRef.current) {
        return;
      }

      if (resetTimerRef.current !== null) {
        window.clearTimeout(resetTimerRef.current);
        resetTimerRef.current = null;
      }

      inputModeRef.current = input;
      setInputMode(input);
      isHoldingRef.current = true;
      setStatus("holding");
      confirmTimerRef.current = window.setTimeout(completeHold, duration);
    },
    [completeHold, disabled, duration, status],
  );

  useEffect(() => {
    return () => {
      clearConfirmTimer();

      if (resetTimerRef.current !== null) {
        window.clearTimeout(resetTimerRef.current);
      }
    };
  }, [clearConfirmTimer]);

  useEffect(() => {
    if (disabled) {
      cancelHold();
    }
  }, [cancelHold, disabled]);

  function releasePointerCapture(pointerId: number) {
    const button = buttonRef.current;

    if (button?.hasPointerCapture(pointerId)) {
      button.releasePointerCapture(pointerId);
    }
  }

  function handlePointerDown(event: PointerEvent<HTMLButtonElement>) {
    if (!event.isPrimary || event.button !== 0 || disabled) {
      return;
    }

    activePointerIdRef.current = event.pointerId;
    event.currentTarget.setPointerCapture(event.pointerId);
    startHold("pointer");
  }

  function handlePointerMove(event: PointerEvent<HTMLButtonElement>) {
    if (
      !isHoldingRef.current ||
      activePointerIdRef.current !== event.pointerId
    ) {
      return;
    }

    const rect = event.currentTarget.getBoundingClientRect();
    const boundaryPadding = 8;
    const isOutside =
      event.clientX < rect.left - boundaryPadding ||
      event.clientX > rect.right + boundaryPadding ||
      event.clientY < rect.top - boundaryPadding ||
      event.clientY > rect.bottom + boundaryPadding;

    if (isOutside) {
      cancelHold();
      releasePointerCapture(event.pointerId);
    }
  }

  function handlePointerEnd(event: PointerEvent<HTMLButtonElement>) {
    if (activePointerIdRef.current !== event.pointerId) {
      return;
    }

    cancelHold();
    releasePointerCapture(event.pointerId);
  }

  function handleKeyDown(event: KeyboardEvent<HTMLButtonElement>) {
    if (event.repeat || (event.key !== "Enter" && event.key !== " ")) {
      return;
    }

    event.preventDefault();
    startHold("keyboard");
  }

  function handleKeyUp(event: KeyboardEvent<HTMLButtonElement>) {
    if (event.key !== "Enter" && event.key !== " ") {
      return;
    }

    event.preventDefault();
    cancelHold();
  }

  const isConfirmed = status === "confirmed";
  const isHolding = status === "holding";
  const overlayStyle = {
    clipPath: isHolding ? "inset(0 0 0 0)" : "inset(0 100% 0 0)",
    transitionDuration:
      shouldReduceMotion || inputMode === "keyboard"
        ? "0ms"
        : isHolding
          ? `${duration}ms`
          : "180ms",
    transitionProperty: "clip-path",
    transitionTimingFunction: isHolding
      ? "linear"
      : "cubic-bezier(0.23, 1, 0.32, 1)",
  };

  return (
    <button
      {...buttonProps}
      aria-busy={isHolding}
      className={cn(
        "relative isolate inline-flex h-9 min-w-40 touch-none cursor-pointer select-none items-center justify-center overflow-hidden rounded-lg border border-red-9 bg-red-3 px-3 font-medium text-red-11 text-sm outline-none transition-[transform,border-color,background-color,color] duration-150 [transition-timing-function:cubic-bezier(0.23,1,0.32,1)] focus-visible:ring-2 focus-visible:ring-red-8 focus-visible:ring-offset-2 focus-visible:ring-offset-grayscale-1 data-[input=pointer]:active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-50 dark:bg-red-4",
        isConfirmed && "bg-red-9 text-white dark:bg-red-9 dark:text-white",
        className,
      )}
      data-input={inputMode}
      disabled={disabled}
      onBlur={cancelHold}
      onKeyDown={handleKeyDown}
      onKeyUp={handleKeyUp}
      onLostPointerCapture={cancelHold}
      onPointerCancel={handlePointerEnd}
      onPointerDown={handlePointerDown}
      onPointerMove={handlePointerMove}
      onPointerUp={handlePointerEnd}
      ref={buttonRef}
      type="button"
    >
      {isConfirmed ? (
        <span className="relative flex items-center justify-center gap-1.5">
          {confirmedContent ?? (
            <>
              <CheckIcon aria-hidden="true" size={15} weight="bold" />
              Confirmed
            </>
          )}
        </span>
      ) : (
        <>
          <span className="relative flex items-center justify-center gap-1.5">
            {children}
          </span>
          <span
            aria-hidden="true"
            className="absolute inset-0 flex items-center justify-center gap-1.5 bg-red-9 px-3 text-white"
            style={overlayStyle}
          >
            {children}
          </span>
        </>
      )}
    </button>
  );
}\