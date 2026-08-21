import { LoginForm } from "@/components/auth/login-form";

export const metadata = {
  title: "Sign in · CareerIQ",
};

export default function LoginPage() {
  return (
    <main className="flex flex-1 items-center justify-center p-6">
      <LoginForm />
    </main>
  );
}
