import { ResumeManager } from "@/components/resume/resume-manager";

export const metadata = {
  title: "My resumes · CareerIQ",
};

export default function ResumesPage() {
  return (
    <main className="flex flex-1 justify-center px-4 py-8 md:px-6">
      <ResumeManager />
    </main>
  );
}
