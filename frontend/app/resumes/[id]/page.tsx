import { ResumeStructure } from "@/components/resume/resume-structure";

export const metadata = {
  title: "Resume structure · CareerIQ",
};

export default async function ResumeStructurePage(
  props: PageProps<"/resumes/[id]">,
) {
  const { id } = await props.params;

  return (
    <main className="flex flex-1 justify-center px-4 py-8 md:px-6">
      <div className="w-full max-w-[720px]">
        <ResumeStructure resumeId={id} />
      </div>
    </main>
  );
}
