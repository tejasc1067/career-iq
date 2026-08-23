import { ProfileForm } from "@/components/profile/profile-form";

export const metadata = {
  title: "My profile · CareerIQ",
};

export default function ProfilePage() {
  return (
    <main className="flex flex-1 justify-center px-4 py-8 md:px-6">
      <ProfileForm />
    </main>
  );
}
