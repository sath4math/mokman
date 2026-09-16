import Link from "next/link";

import { IconArrowRight } from "@/components/icons";
import ui from "@/styles/ui.module.css";

import { howItWorks, ownerBenefits, services, tenantBenefits, trustPoints } from "./home-data";
import { ICON_MAP } from "./icon-map";
import styles from "./page.module.css";

function SectionHeading({ eyebrow, title, body }: { eyebrow: string; title: string; body?: string }) {
  return (
    <div className={styles.sectionHeading}>
      <p className={styles.eyebrow}>{eyebrow}</p>
      <h2 className={styles.sectionTitleText}>{title}</h2>
      {body && <p className={styles.sectionBody}>{body}</p>}
    </div>
  );
}

export default function HomePage() {
  return (
    <main className={styles.main}>
      {/* Hero */}
      <section className={styles.heroSection}>
        <div className={styles.heroInner}>
          <h1 className={styles.heroTitle}>
            Your property, <span className={styles.heroHighlight}>fully managed.</span>
          </h1>
          <p className={styles.heroSubtitle}>
            Mokman handles tenants, rent, maintenance and paperwork — so you don&apos;t have to.
            Hand over the work, keep the ownership.
          </p>
          <div className={styles.heroActions}>
            <Link href="/register" className={ui.btnPrimary}>
              List Your Property
            </Link>
            <Link href="#how-it-works" className={`${ui.btnSecondary} ${styles.secondaryAction}`}>
              See How It Works <IconArrowRight />
            </Link>
          </div>
          <p className={styles.heroTrust}>
            Verified tenants. Digital paperwork. Real support — not a listings board.
          </p>
        </div>
      </section>

      {/* For Owners */}
      <section id="for-owners" className={styles.section}>
        <SectionHeading
          eyebrow="For Owners"
          title="Hand over the work, keep the ownership"
          body="Everything your property needs, run by a team — not a marketplace."
        />
        <div className={styles.ownersImage} aria-hidden="true" />
        <div className={styles.grid4}>
          {ownerBenefits.map((benefit) => {
            const Icon = ICON_MAP[benefit.icon];
            return (
              <div key={benefit.title} className={styles.card}>
                <Icon size={28} className={styles.cardIcon} />
                <h3 className={styles.cardTitle}>{benefit.title}</h3>
                <p className={styles.cardBody}>{benefit.body}</p>
              </div>
            );
          })}
        </div>
        <div className={styles.linkRow}>
          <Link href="/register" className={ui.linkPrimary}>
            List Your Property →
          </Link>
          <Link href="/pricing" className={ui.link}>
            See Owner Packages →
          </Link>
        </div>
      </section>

      {/* For Tenants */}
      <section id="for-tenants" className={styles.sectionMuted}>
        <SectionHeading
          eyebrow="For Tenants"
          title="A home that's actually looked after"
          body="Rent, maintenance, and your lease — all in one place."
        />
        <div className={styles.tenantsImage} aria-hidden="true" />
        <div className={styles.grid4}>
          {tenantBenefits.map((benefit) => {
            const Icon = ICON_MAP[benefit.icon];
            return (
              <div key={benefit.title} className={styles.cardOnSurface}>
                <Icon size={28} className={styles.cardIcon} />
                <h3 className={styles.cardTitle}>{benefit.title}</h3>
                <p className={styles.cardBody}>{benefit.body}</p>
              </div>
            );
          })}
        </div>
        <div className={styles.linkRowSingle}>
          <Link href="/register" className={ui.linkPrimary}>
            Create your tenant account →
          </Link>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className={styles.section}>
        <SectionHeading eyebrow="How It Works" title="From registration to reporting" />
        <div className={styles.howItWorksImage} aria-hidden="true" />
        <div className={styles.stepsGrid}>
          {howItWorks.map((item) => (
            <div key={item.step} className={styles.step}>
              <div className={styles.stepBadge}>{item.step}</div>
              <h3 className={styles.cardTitle}>{item.title}</h3>
              <p className={styles.cardBody}>{item.body}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Services */}
      <section id="services" className={styles.sectionMuted}>
        <SectionHeading eyebrow="Services" title="Everything a property needs" />
        <div className={styles.servicesImage} aria-hidden="true" />
        <div className={styles.grid3}>
          {services.map((service) => {
            const Icon = ICON_MAP[service.icon];
            return (
              <div key={service.title} className={styles.serviceCard}>
                <Icon size={24} className={styles.serviceIcon} />
                <div>
                  <h3 className={styles.cardTitle}>{service.title}</h3>
                  <p className={styles.cardBody}>{service.body}</p>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* Packages preview */}
      <section className={styles.section}>
        <SectionHeading
          eyebrow="Pricing"
          title="A package for every level of hands-off"
          body="From self-serve record-keeping to a fully managed portfolio."
        />
        <div className={styles.pricingImage} aria-hidden="true" />
        <div className={styles.pillRow}>
          {["Starter", "Managed", "Full Care", "Complete"].map((tier) => (
            <span key={tier} className={styles.pill}>
              {tier}
            </span>
          ))}
        </div>
        <div className={styles.ctaCenter}>
          <Link href="/pricing" className={ui.btnPrimary}>
            Compare all packages
          </Link>
        </div>
      </section>

      {/* Trust & Compliance */}
      <section className={styles.sectionMuted}>
        <SectionHeading eyebrow="Trust & Compliance" title="Built to be trusted with your property" />
        <div className={styles.trustImage} aria-hidden="true" />
        <ul className={styles.trustList}>
          {trustPoints.map((point) => (
            <li key={point} className={styles.trustItem}>
              <span className={styles.trustDot} />
              {point}
            </li>
          ))}
        </ul>
      </section>

      {/* Final CTA */}
      <section className={styles.finalCta}>
        <h2 className={styles.finalCtaTitle}>Ready to hand over the work?</h2>
        <p className={styles.finalCtaBody}>
          List your property in a few minutes and see what Mokman handles for you.
        </p>
        <div className={styles.ctaCenter}>
          <Link href="/register" className={ui.btnPrimary}>
            List Your Property
          </Link>
        </div>
      </section>
    </main>
  );
}
