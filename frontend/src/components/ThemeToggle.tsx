import { Moon, Sun, Monitor, Check } from 'lucide-react';
import { Button } from './ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from './ui/dropdown-menu';
import { useThemeStore, type Theme } from '../stores/theme';

export function ThemeToggle() {
  const { theme, setTheme } = useThemeStore();

  const themes: { value: Theme; label: string; icon: typeof Sun }[] = [
    { value: 'light', label: 'Light', icon: Sun },
    { value: 'dark', label: 'Dark', icon: Moon },
    { value: 'system', label: 'System', icon: Monitor },
  ];

  const currentTheme = themes.find((t) => t.value === theme) || themes[2];
  const Icon = currentTheme.icon;

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          className="h-9 w-9 transition-all duration-200 hover:rotate-12"
          aria-label="Toggle theme"
        >
          <Icon className="h-4 w-4 transition-transform" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-40 animate-slide-in-from-top">
        {themes.map(({ value, label, icon: ThemeIcon }) => (
          <DropdownMenuItem
            key={value}
            onClick={() => setTheme(value)}
            className="flex items-center gap-2 cursor-pointer"
          >
            <ThemeIcon className="h-4 w-4" />
            <span className="flex-1">{label}</span>
            {theme === value && (
              <Check className="h-4 w-4 text-primary" />
            )}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
