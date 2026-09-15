import {
  IconBuilding,
  IconClipboardCheck,
  IconFileText,
  IconScale,
  IconShieldCheck,
  IconUmbrella,
  IconWallet,
  IconWrench,
} from "@/components/icons";

export const ICON_MAP = {
  shield: IconShieldCheck,
  wallet: IconWallet,
  wrench: IconWrench,
  file: IconFileText,
  building: IconBuilding,
  clipboard: IconClipboardCheck,
  umbrella: IconUmbrella,
  scale: IconScale,
} as const;

export type IconName = keyof typeof ICON_MAP;
