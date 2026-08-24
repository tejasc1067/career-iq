"use client";

import { Badge } from "@/components/ui/badge";
import type { StructuredResume } from "@/lib/api/resumes";

function dateRange(start: string | null, end: string | null, current: boolean) {
  const finish = current ? "Present" : end;
  if (!start && !finish) {
    return null;
  }
  return [start, finish].filter(Boolean).join(" – ");
}

function Section({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <section className="space-y-2">
      <h3 className="font-heading text-sm font-semibold">{title}</h3>
      {children}
    </section>
  );
}

export function ResumeUnderstanding({
  understanding,
}: {
  understanding: StructuredResume;
}) {
  const { contact } = understanding;
  const details = [
    contact.email,
    contact.phone,
    contact.location,
    contact.linkedin_url,
    contact.github_url,
  ].filter(Boolean);
  const skills = understanding.skills.filter((skill) => skill.name);
  const empty =
    !contact.full_name &&
    details.length === 0 &&
    !understanding.professional_summary &&
    understanding.experience.length === 0 &&
    skills.length === 0 &&
    understanding.education.length === 0 &&
    understanding.projects.length === 0 &&
    understanding.certifications.length === 0;

  if (empty) {
    return (
      <p className="text-muted-foreground text-sm">
        CareerIQ read this resume but found nothing it could structure.
      </p>
    );
  }

  return (
    <div className="space-y-5">
      {(contact.full_name || details.length > 0) && (
        <Section title="Contact">
          {contact.full_name && (
            <p className="text-sm font-medium">{contact.full_name}</p>
          )}
          {details.length > 0 && (
            <p className="text-muted-foreground text-xs">
              {details.join(" · ")}
            </p>
          )}
        </Section>
      )}

      {understanding.professional_summary && (
        <Section title="Summary">
          <p className="text-sm">{understanding.professional_summary}</p>
        </Section>
      )}

      {understanding.experience.length > 0 && (
        <Section title="Experience">
          <ul className="space-y-3">
            {understanding.experience.map((role, index) => (
              <li key={`${role.company}-${role.role}-${index}`}>
                <p className="text-sm font-medium">
                  {[role.role, role.company].filter(Boolean).join(" · ")}
                </p>
                <p className="text-muted-foreground text-xs">
                  {[
                    dateRange(role.start_date, role.end_date, role.is_current),
                    role.location,
                  ]
                    .filter(Boolean)
                    .join(" · ")}
                </p>
                {role.highlights.length > 0 && (
                  <ul className="mt-1 list-disc space-y-0.5 pl-5 text-sm">
                    {role.highlights.map((highlight) => (
                      <li key={highlight}>{highlight}</li>
                    ))}
                  </ul>
                )}
              </li>
            ))}
          </ul>
        </Section>
      )}

      {skills.length > 0 && (
        <Section title="Skills">
          <ul className="flex flex-wrap gap-1.5">
            {skills.map((skill, index) => (
              <li key={`${skill.name}-${index}`}>
                <Badge variant="secondary">
                  {skill.category ? `${skill.name} · ${skill.category}` : skill.name}
                </Badge>
              </li>
            ))}
          </ul>
        </Section>
      )}

      {understanding.education.length > 0 && (
        <Section title="Education">
          <ul className="space-y-2">
            {understanding.education.map((entry, index) => (
              <li key={`${entry.institution}-${index}`}>
                <p className="text-sm font-medium">
                  {[entry.degree, entry.field_of_study]
                    .filter(Boolean)
                    .join(", ") || entry.institution}
                </p>
                <p className="text-muted-foreground text-xs">
                  {[
                    entry.degree || entry.field_of_study
                      ? entry.institution
                      : null,
                    dateRange(entry.start_date, entry.end_date, false),
                  ]
                    .filter(Boolean)
                    .join(" · ")}
                </p>
              </li>
            ))}
          </ul>
        </Section>
      )}

      {understanding.projects.length > 0 && (
        <Section title="Projects">
          <ul className="space-y-2">
            {understanding.projects.map((project, index) => (
              <li key={`${project.name}-${index}`}>
                <p className="text-sm font-medium">{project.name}</p>
                {project.description && (
                  <p className="text-sm">{project.description}</p>
                )}
                {project.technologies.length > 0 && (
                  <p className="text-muted-foreground text-xs">
                    {project.technologies.join(" · ")}
                  </p>
                )}
              </li>
            ))}
          </ul>
        </Section>
      )}

      {understanding.certifications.length > 0 && (
        <Section title="Certifications">
          <ul className="space-y-1">
            {understanding.certifications.map((certification, index) => (
              <li key={`${certification.name}-${index}`}>
                <p className="text-sm font-medium">{certification.name}</p>
                <p className="text-muted-foreground text-xs">
                  {[certification.issuing_organization, certification.date]
                    .filter(Boolean)
                    .join(" · ")}
                </p>
              </li>
            ))}
          </ul>
        </Section>
      )}
    </div>
  );
}
