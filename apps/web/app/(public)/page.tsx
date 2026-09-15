import Link from "next/link";

import { IconArrowRight } from "@/components/icons";

import { howItWorks, ownerBenefits, services, tenantBenefits, trustPoints } from "./home-data";
import { ICON_MAP } from "./icon-map";

function SectionHeading({ eyebrow, title, body }: { eyebrow: string; title: string; body?: string }) {
  return (
    <div className="mx-auto max-w-2xl text-center">
      <p className="text-sm font-semibold uppercase tracking-wide text-emerald-700 dark:text-emerald-400">
        {eyebrow}
      </p>
      <h2 className="mt-2 text-3xl font-semibold tracking-tight">{title}</h2>
      {body && <p className="mt-3 text-zinc-600 dark:text-zinc-400">{body}</p>}
    </div>
  );
}

export default function HomePage() {
  return (
    <main className="flex flex-1 flex-col">
      {/* Hero */}
      <section className="bg-gradient-to-b from-emerald-50 to-white px-6 py-24 dark:from-emerald-950/20 dark:to-zinc-950">
        <div className="mx-auto flex max-w-3xl flex-col items-center gap-6 text-center">
          <h1 className="text-4xl font-bold tracking-tight sm:text-5xl">
            Your property, <span className="text-emerald-700 dark:text-emerald-400">fully managed.</span>
          </h1>
          <p className="max-w-xl text-lg text-zinc-600 dark:text-zinc-400">
            Mokman handles tenants, rent, maintenance and paperwork — so you don&apos;t have to.
            Hand over the work, keep the ownership.
          </p>
          <div className="flex flex-wrap items-center justify-center gap-4">
            <Link
              href="/register"
              className="rounded-full bg-emerald-600 px-6 py-3 font-semibold text-white shadow-sm hover:bg-emerald-700"
            >
              List Your Property
            </Link>
            <Link
              href="#how-it-works"
              className="flex items-center gap-1 rounded-full border border-zinc-300 px-6 py-3 font-semibold hover:border-zinc-400 dark:border-zinc-700 dark:hover:border-zinc-600"
            >
              See How It Works <IconArrowRight />
            </Link>
          </div>
          <p className="text-sm text-zinc-500 dark:text-zinc-500">
            Verified tenants. Digital paperwork. Real support — not a listings board.
          </p>
        </div>
      </section>

      {/* For Owners */}
      <section id="for-owners" className="px-6 py-20">
        <SectionHeading
          eyebrow="For Owners"
          title="Hand over the work, keep the ownership"
          body="Everything your property needs, run by a team — not a marketplace."
        />
        <div className="mx-auto mt-12 grid max-w-5xl grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {ownerBenefits.map((benefit) => {
            const Icon = ICON_MAP[benefit.icon];
            return (
              <div
                key={benefit.title}
                className="flex flex-col gap-3 rounded-2xl border border-zinc-200 p-6 dark:border-zinc-800"
              >
                <Icon className="h-7 w-7 text-emerald-600 dark:text-emerald-400" />
                <h3 className="font-semibold">{benefit.title}</h3>
                <p className="text-sm text-zinc-600 dark:text-zinc-400">{benefit.body}</p>
              </div>
            );
          })}
        </div>
        <div className="mt-10 flex justify-center gap-6 text-sm">
          <Link href="/register" className="font-semibold text-emerald-700 hover:underline dark:text-emerald-400">
            List Your Property →
          </Link>
          <Link href="/pricing" className="font-semibold hover:underline">
            See Owner Packages →
          </Link>
        </div>
      </section>

      {/* For Tenants */}
      <section id="for-tenants" className="bg-zinc-50 px-6 py-20 dark:bg-zinc-900/40">
        <SectionHeading
          eyebrow="For Tenants"
          title="A home that's actually looked after"
          body="Rent, maintenance, and your lease — all in one place."
        />
        <div className="mx-auto mt-12 grid max-w-5xl grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {tenantBenefits.map((benefit) => {
            const Icon = ICON_MAP[benefit.icon];
            return (
              <div
                key={benefit.title}
                className="flex flex-col gap-3 rounded-2xl border border-zinc-200 bg-white p-6 dark:border-zinc-800 dark:bg-zinc-950"
              >
                <Icon className="h-7 w-7 text-emerald-600 dark:text-emerald-400" />
                <h3 className="font-semibold">{benefit.title}</h3>
                <p className="text-sm text-zinc-600 dark:text-zinc-400">{benefit.body}</p>
              </div>
            );
          })}
        </div>
        <div className="mt-10 flex justify-center">
          <Link href="/register" className="font-semibold text-emerald-700 hover:underline dark:text-emerald-400">
            Create your tenant account →
          </Link>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="px-6 py-20">
        <SectionHeading eyebrow="How It Works" title="From registration to reporting" />
        <div className="mx-auto mt-12 grid max-w-5xl grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-4">
          {howItWorks.map((item) => (
            <div key={item.step} className="flex flex-col gap-2">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-emerald-600 font-semibold text-white">
                {item.step}
              </div>
              <h3 className="font-semibold">{item.title}</h3>
              <p className="text-sm text-zinc-600 dark:text-zinc-400">{item.body}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Services */}
      <section id="services" className="bg-zinc-50 px-6 py-20 dark:bg-zinc-900/40">
        <SectionHeading eyebrow="Services" title="Everything a property needs" />
        <div className="mx-auto mt-12 grid max-w-5xl grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {services.map((service) => {
            const Icon = ICON_MAP[service.icon];
            return (
              <div
                key={service.title}
                className="flex items-start gap-4 rounded-2xl border border-zinc-200 bg-white p-6 dark:border-zinc-800 dark:bg-zinc-950"
              >
                <Icon className="h-6 w-6 shrink-0 text-emerald-600 dark:text-emerald-400" />
                <div>
                  <h3 className="font-semibold">{service.title}</h3>
                  <p className="text-sm text-zinc-600 dark:text-zinc-400">{service.body}</p>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* Packages preview */}
      <section className="px-6 py-20">
        <SectionHeading
          eyebrow="Pricing"
          title="A package for every level of hands-off"
          body="From self-serve record-keeping to a fully managed portfolio."
        />
        <div className="mx-auto mt-10 flex max-w-3xl flex-wrap justify-center gap-3">
          {["Starter", "Managed", "Full Care", "Complete"].map((tier) => (
            <span
              key={tier}
              className="rounded-full border border-zinc-300 px-4 py-2 text-sm font-medium dark:border-zinc-700"
            >
              {tier}
            </span>
          ))}
        </div>
        <div className="mt-8 flex justify-center">
          <Link
            href="/pricing"
            className="rounded-full bg-emerald-600 px-6 py-3 font-semibold text-white shadow-sm hover:bg-emerald-700"
          >
            Compare all packages
          </Link>
        </div>
      </section>

      {/* Trust & Compliance */}
      <section className="bg-zinc-50 px-6 py-20 dark:bg-zinc-900/40">
        <SectionHeading eyebrow="Trust & Compliance" title="Built to be trusted with your property" />
        <ul className="mx-auto mt-10 flex max-w-2xl flex-col gap-3">
          {trustPoints.map((point) => (
            <li key={point} className="flex items-center gap-3 text-sm text-zinc-700 dark:text-zinc-300">
              <span className="h-1.5 w-1.5 shrink-0 rounded-full bg-emerald-600" />
              {point}
            </li>
          ))}
        </ul>
      </section>

      {/* Final CTA */}
      <section className="px-6 py-20 text-center">
        <h2 className="text-3xl font-semibold tracking-tight">Ready to hand over the work?</h2>
        <p className="mx-auto mt-3 max-w-xl text-zinc-600 dark:text-zinc-400">
          List your property in a few minutes and see what Mokman handles for you.
        </p>
        <div className="mt-8">
          <Link
            href="/register"
            className="rounded-full bg-emerald-600 px-6 py-3 font-semibold text-white shadow-sm hover:bg-emerald-700"
          >
            List Your Property
          </Link>
        </div>
      </section>
    </main>
  );
}
