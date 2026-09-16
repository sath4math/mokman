import { redirect } from "next/navigation";

import { LogoutButton } from "@/components/logout-button";
import { getCurrentUser } from "@/lib/current-user";
import ui from "@/styles/ui.module.css";

import { OwnerAssistantPanel } from "./owner-assistant-panel";
import styles from "./assistant.module.css";

export default async function OwnerAssistantPage() {
  const user = await getCurrentUser();
  if (!user) redirect("/login");

  return (
    <main className={styles.main}>
      <div className={ui.flexBetween}>
        <h1 className={styles.title}>Owner Assistant</h1>
        <LogoutButton />
      </div>
      <OwnerAssistantPanel />
    </main>
  );
}
