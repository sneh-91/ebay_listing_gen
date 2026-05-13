import type { BuyerQuestion } from "../types/listing";

type BuyerQuestionsCardProps = {
  questions: BuyerQuestion[];
};

export function BuyerQuestionsCard({ questions }: BuyerQuestionsCardProps) {
  return (
    <section className="rounded-[1.75rem] border border-white/10 bg-surface/80 p-6">
      <p className="text-sm uppercase tracking-[0.25em] text-muted">
        Buyer Q&A
      </p>
      <div className="mt-4 space-y-4">
        {questions.map((question) => (
          <article
            key={question.question}
            className="rounded-2xl border border-white/8 bg-surfaceAlt/70 p-4"
          >
            <h3 className="text-sm font-medium text-text">{question.question}</h3>
            <p className="mt-2 text-sm leading-6 text-muted">{question.answer}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
