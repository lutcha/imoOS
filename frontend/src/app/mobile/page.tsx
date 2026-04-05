import { redirect } from "next/navigation";

/**
 * Mobile Root — Redirect to obra dashboard
 */
export default function MobilePage() {
  redirect("/mobile/obra");
}
