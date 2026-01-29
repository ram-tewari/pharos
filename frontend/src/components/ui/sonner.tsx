import { Toaster as Sonner } from "sonner"

type ToasterProps = React.ComponentProps<typeof Sonner>

const Toaster = ({ ...props }: ToasterProps) => {
  return (
    <Sonner
      className="toaster group"
      position="top-right"
      toastOptions={{
        classNames: {
          toast:
            "group toast group-[.toaster]:bg-card group-[.toaster]:text-foreground group-[.toaster]:border-border group-[.toaster]:shadow-lg group-[.toaster]:rounded-lg animate-slide-in-from-top",
          description: "group-[.toast]:text-muted-foreground group-[.toast]:text-sm",
          actionButton:
            "group-[.toast]:bg-primary group-[.toast]:text-primary-foreground group-[.toast]:hover:bg-primary/90 group-[.toast]:transition-all",
          cancelButton:
            "group-[.toast]:bg-muted group-[.toast]:text-muted-foreground group-[.toast]:hover:bg-muted/80 group-[.toast]:transition-all",
          success: "group-[.toast]:border-[hsl(var(--success))]/50 group-[.toast]:bg-[hsl(var(--success))]/10",
          error: "group-[.toast]:border-destructive/50 group-[.toast]:bg-destructive/10",
          warning: "group-[.toast]:border-[hsl(var(--warning))]/50 group-[.toast]:bg-[hsl(var(--warning))]/10",
          info: "group-[.toast]:border-[hsl(var(--info))]/50 group-[.toast]:bg-[hsl(var(--info))]/10",
        },
      }}
      {...props}
    />
  )
}

export { Toaster }
